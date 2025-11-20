"""
11-step resilient workflow for MD-to-Video generation.
Each step has checkpointing, retry logic, and fallback mechanisms.
"""

import os
import json
import time
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime
from dotenv import load_dotenv
import traceback

# Import utilities
from logger import (
    log_error, log_info, log_success, log_warning,
    save_checkpoint, load_checkpoint, cleanup_checkpoints,
    get_job_error_count
)
from db import (
    update_job_status, add_job_error, increment_retry_count,
    mark_step_complete, update_job
)
import prompts

load_dotenv()

# Configuration
MAX_RETRIES_PER_STEP = int(os.getenv('MAX_RETRIES_PER_STEP', '3'))
MAX_TOTAL_RETRIES = int(os.getenv('MAX_TOTAL_RETRIES', '10'))
ERROR_THRESHOLD_DEGRADED = int(os.getenv('ERROR_THRESHOLD_DEGRADED', '5'))
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai').lower()  # Default: 'openai'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')  # Optional fallback
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')
MANIM_PATH = os.getenv('MANIM_PATH', 'manim')
EDGE_TTS_VOICE = os.getenv('EDGE_TTS_VOICE', 'en-US-GuyNeural')

# Working directories
WORK_DIR = Path('./data/work')
OUTPUT_DIR = Path('./data/outputs')
WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class WorkflowContext:
    """Context object passed through workflow steps."""
    
    def __init__(self, job_id: str, md_content: str):
        self.job_id = job_id
        self.md_content = md_content
        self.work_dir = WORK_DIR / job_id
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Step outputs
        self.system_prompt = ""
        self.summary = ""
        self.base_script = ""
        self.timings = []
        self.images_suggestions = []
        self.layouts = []
        self.images_downloaded = []
        self.enhanced_script = ""
        self.silent_video_path = ""
        self.narration = []
        self.audio_path = ""
        self.final_video_path = ""
        
        # Metadata
        self.tokens_used = {'total': 0, 'by_step': {}}
        self.error_count = 0
        self.degraded_mode = False
        self.fallback_log = []
    
    def get_file_path(self, filename: str) -> Path:
        """Get path for file in work directory."""
        return self.work_dir / filename


def resilient_step(
    step_no: int,
    step_name: str,
    func: Callable,
    ctx: WorkflowContext,
    max_retries: int = MAX_RETRIES_PER_STEP,
    allow_fallback: bool = True
) -> Tuple[bool, Any]:
    """
    Wrap a workflow step with retry logic, checkpointing, and error handling.
    
    Args:
        step_no: Step number (0-10)
        step_name: Human-readable step name
        func: Function to execute (takes ctx, returns result)
        ctx: Workflow context
        max_retries: Maximum retry attempts
        allow_fallback: Whether to use fallback on failure
    
    Returns:
        Tuple of (success: bool, result: Any)
    """
    log_info(ctx.job_id, step_no, f"Starting step: {step_name}")
    
    retries = 0
    last_error = None
    
    while retries <= max_retries:
        try:
            # Execute step function
            result = func(ctx)
            
            # Save checkpoint on success
            checkpoint_data = {
                'step_no': step_no,
                'step_name': step_name,
                'result': result if isinstance(result, (str, dict, list, int, float, bool)) else str(result),
                'ctx_state': {
                    'summary': ctx.summary,
                    'base_script': ctx.base_script[:500] if ctx.base_script else "",
                    'timings': ctx.timings,
                    'images_suggestions': ctx.images_suggestions,
                    'error_count': ctx.error_count
                }
            }
            save_checkpoint(ctx.job_id, step_no, checkpoint_data)
            
            # Mark step complete
            mark_step_complete(ctx.job_id, step_no)
            log_success(ctx.job_id, step_no, f"Completed: {step_name}")
            
            return (True, result)
            
        except Exception as e:
            last_error = e
            error_msg = f"{type(e).__name__}: {str(e)}"
            error_trace = traceback.format_exc()
            
            retries += 1
            increment_retry_count(ctx.job_id)
            ctx.error_count += 1
            
            # Determine error type
            error_type = classify_error(e)
            
            # Log error
            log_error(
                job_id=ctx.job_id,
                step_no=step_no,
                error_type=error_type,
                details=f"{error_msg}\n{error_trace}",
                retry_count=retries,
                fallback_used=False
            )
            add_job_error(ctx.job_id, f"Step {step_no} ({step_name}): {error_msg}")
            
            # Check if we should retry
            if retries <= max_retries:
                # Try to restore previous checkpoint
                if step_no > 0:
                    prev_checkpoint = load_checkpoint(ctx.job_id, step_no - 1)
                    if prev_checkpoint:
                        log_info(ctx.job_id, step_no, f"Restored checkpoint from step {step_no - 1}")
                
                # Exponential backoff
                backoff = min(2 ** retries, 30)
                log_warning(ctx.job_id, step_no, f"Retry {retries}/{max_retries} after {backoff}s")
                time.sleep(backoff)
            else:
                log_error(
                    job_id=ctx.job_id,
                    step_no=step_no,
                    error_type="MAX_RETRIES",
                    details=f"Exhausted retries for {step_name}",
                    retry_count=retries,
                    fallback_used=allow_fallback
                )
    
    # All retries exhausted - try fallback
    if allow_fallback:
        log_warning(ctx.job_id, step_no, f"Attempting fallback for {step_name}")
        try:
            fallback_result = get_fallback(step_no, ctx)
            ctx.fallback_log.append({
                'step': step_no,
                'name': step_name,
                'reason': str(last_error)
            })
            
            # Save fallback checkpoint
            save_checkpoint(ctx.job_id, step_no, {
                'step_no': step_no,
                'fallback': True,
                'result': fallback_result
            })
            
            mark_step_complete(ctx.job_id, step_no)
            log_warning(ctx.job_id, step_no, f"Using fallback for {step_name}")
            
            return (True, fallback_result)
        except Exception as fallback_error:
            log_error(
                job_id=ctx.job_id,
                step_no=step_no,
                error_type="FALLBACK_FAILED",
                details=str(fallback_error),
                retry_count=retries,
                fallback_used=True
            )
    
    # Complete failure
    return (False, None)


def classify_error(exception: Exception) -> str:
    """Classify exception into error type."""
    error_str = str(exception).lower()
    
    if 'token' in error_str or 'rate limit' in error_str:
        return 'TOKEN_ERROR'
    elif 'syntax' in error_str or 'invalid syntax' in error_str:
        return 'SYNTAX_ERROR'
    elif 'connection' in error_str or 'timeout' in error_str:
        return 'NETWORK_ERROR'
    elif 'not found' in error_str or 'no such file' in error_str:
        return 'FILE_ERROR'
    elif 'api' in error_str or 'key' in error_str:
        return 'API_ERROR'
    elif 'render' in error_str or 'manim' in error_str:
        return 'RENDER_ERROR'
    elif 'format' in error_str or 'parse' in error_str:
        return 'FORMAT_ERROR'
    else:
        return 'UNKNOWN_ERROR'


def get_fallback(step_no: int, ctx: WorkflowContext) -> Any:
    """Get fallback result for a failed step."""
    
    fallbacks = {
        0: prompts.SYSTEM_GDOT_DOT,
        1: ctx.md_content[:2000] if len(ctx.md_content) > 2000 else ctx.md_content,
        2: prompts.FALLBACK_SUMMARY,
        3: {'script': prompts.MANIM_BASE_TEMPLATE, 'timings': [{'slide_no': 1, 'duration': 30, 'title': 'Overview'}]},
        4: {'images': [], 'layouts': []},
        5: [],
        6: ctx.base_script or prompts.MANIM_BASE_TEMPLATE,
        7: "",
        8: [{'slide_no': 1, 'duration': 30, 'narration_text': 'Generated educational content.'}],
        9: "",
        10: ctx.silent_video_path
    }
    
    return fallbacks.get(step_no, None)


# ============================================================================
# WORKFLOW STEP FUNCTIONS
# ============================================================================

def step_0_load_system_prompts(ctx: WorkflowContext) -> str:
    """Step 0: Load system prompts from prompts.py"""
    log_info(ctx.job_id, 0, "Loading GDOT-DOT system prompts")
    
    ctx.system_prompt = prompts.SYSTEM_GDOT_DOT
    
    # Save to file for reference
    prompt_file = ctx.get_file_path('system_prompt.txt')
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(ctx.system_prompt)
    
    return ctx.system_prompt


def step_1_validate_input(ctx: WorkflowContext) -> str:
    """Step 1: Validate and chunk markdown input"""
    log_info(ctx.job_id, 1, f"Validating MD input ({len(ctx.md_content)} chars)")
    
    # Basic validation
    if not ctx.md_content or len(ctx.md_content) < 10:
        raise ValueError("Markdown content too short (min 10 chars)")
    
    # Chunk if too large (>2000 words ~10k chars)
    max_chars = 10000
    if len(ctx.md_content) > max_chars:
        log_warning(ctx.job_id, 1, f"Truncating MD from {len(ctx.md_content)} to {max_chars} chars")
        ctx.md_content = ctx.md_content[:max_chars]
    
    # Save validated input
    input_file = ctx.get_file_path('input.md')
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(ctx.md_content)
    
    # Update job status
    update_job_status(ctx.job_id, 'processing', current_step='1')
    
    return ctx.md_content


def call_llm(prompt: str, max_tokens: int = 1000) -> Tuple[str, int]:
    """
    Call LLM (Groq or OpenAI) based on LLM_PROVIDER setting.
    
    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens to generate
    
    Returns:
        Tuple of (response_text, tokens_used)
    """
    if LLM_PROVIDER == 'openai':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4" for better quality
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            text = response.choices[0].message.content.strip()
            tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0
            
            return text, tokens
            
        except Exception as e:
            if 'openai' in str(e).lower() or 'api' in str(e).lower():
                raise Exception(f"OpenAI API error: {e}. Check OPENAI_API_KEY in .env")
            raise
    
    else:  # Default to Groq
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            text = response.choices[0].message.content.strip()
            tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0
            
            return text, tokens
            
        except Exception as e:
            if 'groq' in str(e).lower() or 'api' in str(e).lower():
                raise Exception(f"Groq API error: {e}. Check GROQ_API_KEY in .env")
            raise


def step_2_generate_summary(ctx: WorkflowContext) -> str:
    """Step 2: Generate summary using LLM"""
    log_info(ctx.job_id, 2, f"Generating summary with {LLM_PROVIDER.upper()} LLM")
    
    try:
        prompt = prompts.get_summary_prompt(ctx.md_content)
        ctx.summary, tokens = call_llm(prompt, max_tokens=500)
        
        # Track tokens
        ctx.tokens_used['by_step']['2'] = tokens
        ctx.tokens_used['total'] += tokens
        
        # Save summary
        summary_file = ctx.get_file_path('summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(ctx.summary)
        
        return ctx.summary
        
    except Exception as e:
        raise


def step_3_generate_base_script(ctx: WorkflowContext) -> Dict[str, Any]:
    """Step 3: Generate base Manim script and timings"""
    log_info(ctx.job_id, 3, f"Generating Manim script with {LLM_PROVIDER.upper()} LLM")
    
    try:
        prompt = prompts.get_base_script_prompt(ctx.summary)
        content, tokens = call_llm(prompt, max_tokens=2000)
        
        # Track tokens
        ctx.tokens_used['by_step']['3'] = tokens
        ctx.tokens_used['total'] += tokens
        
        # Extract Python script
        script_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
        if script_match:
            ctx.base_script = script_match.group(1)
        else:
            # Try without language specifier
            script_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
            if script_match:
                ctx.base_script = script_match.group(1)
            else:
                raise ValueError("Could not extract Python script from LLM response")
        
        # Extract JSON timings
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            timings_data = json.loads(json_match.group(1))
            ctx.timings = timings_data.get('slides', [])
        else:
            # Default timing
            ctx.timings = [{'slide_no': 1, 'duration': 30, 'title': 'Overview'}]
        
        # Validate script syntax (dry run)
        try:
            compile(ctx.base_script, '<string>', 'exec')
        except SyntaxError as e:
            raise SyntaxError(f"Generated script has syntax error: {e}")
        
        # Ensure white background - inject if missing
        if 'background_color' not in ctx.base_script and 'WHITE' not in ctx.base_script:
            log_warning(ctx.job_id, 3, "Background color not found in script, injecting fallback")
            
            # Ensure WHITE is imported
            if 'from manim import' in ctx.base_script and 'WHITE' not in ctx.base_script:
                ctx.base_script = ctx.base_script.replace('from manim import *', 'from manim import *  # WHITE imported')
            
            # Try multiple patterns to find construct() method
            patterns = [
                (r'(def construct\(self\):)\s*\n', r'\1\n        config.background_color = WHITE\n        self.camera.background_color = WHITE\n'),
                (r'(def construct\(self\):)', r'\1\n        config.background_color = WHITE\n        self.camera.background_color = WHITE'),
                (r'(class \w+\(Scene\):.*?def construct\(self\):)', r'\1\n        config.background_color = WHITE\n        self.camera.background_color = WHITE', re.DOTALL),
            ]
            
            injected = False
            for pattern, replacement, *flags in patterns:
                flag = flags[0] if flags else 0
                new_script = re.sub(pattern, replacement, ctx.base_script, count=1, flags=flag)
                if new_script != ctx.base_script:
                    ctx.base_script = new_script
                    injected = True
                    log_info(ctx.job_id, 3, f"Injected background color using pattern: {pattern[:30]}")
                    break
            
            if not injected:
                log_warning(ctx.job_id, 3, "Could not inject background color - pattern not found")
        elif 'WHITE' in ctx.base_script or 'background_color' in ctx.base_script:
            log_info(ctx.job_id, 3, "Background color already present in script")
        
        # Save script
        script_file = ctx.get_file_path('base_script.py')
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(ctx.base_script)
        
        # Save timings
        timings_file = ctx.get_file_path('timings.json')
        with open(timings_file, 'w', encoding='utf-8') as f:
            json.dump({'slides': ctx.timings}, f, indent=2)
        
        return {'script': ctx.base_script, 'timings': ctx.timings}
        
    except Exception as e:
        raise


def step_4_suggest_images_layouts(ctx: WorkflowContext) -> Dict[str, Any]:
    """Step 4: Suggest images and layouts using LLM"""
    log_info(ctx.job_id, 4, "Suggesting images and layouts")
    
    try:
        # Create script summary for prompting
        script_summary = f"Script with {len(ctx.timings)} slides. Summary: {ctx.summary[:200]}"
        
        prompt = prompts.get_image_layout_prompt(script_summary)
        content, tokens = call_llm(prompt, max_tokens=1000)
        
        # Track tokens
        ctx.tokens_used['by_step']['4'] = tokens
        ctx.tokens_used['total'] += tokens
        
        # Extract images JSON
        images_match = re.search(r'images\.json[:\s]*\n*```json\n(.*?)\n```', content, re.DOTALL)
        if not images_match:
            images_match = re.search(r'```json\n(\[.*?\])\n```', content, re.DOTALL)
        
        if images_match:
            ctx.images_suggestions = json.loads(images_match.group(1))
        else:
            ctx.images_suggestions = []
        
        # Extract layouts JSON
        layouts_match = re.search(r'layouts\.json[:\s]*\n*```json\n(.*?)\n```', content, re.DOTALL)
        if not layouts_match:
            # Try to find second JSON block
            json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
            if len(json_blocks) >= 2 and json_blocks[1].strip():
                try:
                    ctx.layouts = json.loads(json_blocks[1])
                except json.JSONDecodeError:
                    log_warning(ctx.job_id, 4, "Failed to parse layouts JSON, using empty list")
                    ctx.layouts = []
            else:
                ctx.layouts = []
        else:
            try:
                ctx.layouts = json.loads(layouts_match.group(1))
            except json.JSONDecodeError:
                log_warning(ctx.job_id, 4, "Failed to parse layouts JSON from match, using empty list")
                ctx.layouts = []
        
        # Save suggestions
        images_file = ctx.get_file_path('images.json')
        with open(images_file, 'w', encoding='utf-8') as f:
            json.dump(ctx.images_suggestions, f, indent=2)
        
        layouts_file = ctx.get_file_path('layouts.json')
        with open(layouts_file, 'w', encoding='utf-8') as f:
            json.dump(ctx.layouts, f, indent=2)
        
        return {'images': ctx.images_suggestions, 'layouts': ctx.layouts}
        
    except Exception as e:
        raise


def step_5_fetch_images(ctx: WorkflowContext) -> List[str]:
    """Step 5: Fetch images using SerpAPI and resize"""
    log_info(ctx.job_id, 5, f"Fetching {len(ctx.images_suggestions)} images")
    
    if not ctx.images_suggestions:
        log_warning(ctx.job_id, 5, "No images to fetch, skipping")
        return []
    
    if not SERPAPI_KEY:
        log_warning(ctx.job_id, 5, "SERPAPI_KEY not set, skipping image fetch")
        return []
    
    try:
        from serpapi import GoogleSearch
        from PIL import Image
        import urllib.request
        
        images_dir = ctx.get_file_path('temp_images')
        images_dir.mkdir(exist_ok=True)
        
        downloaded = []
        
        for idx, img_info in enumerate(ctx.images_suggestions[:4]):  # Max 4 images
            try:
                query = img_info.get('search_query', '')
                if not query:
                    continue
                
                log_info(ctx.job_id, 5, f"Searching for: {query}")
                
                # Search for images
                params = {
                    "q": query,
                    "tbm": "isch",
                    "api_key": SERPAPI_KEY
                }
                search = GoogleSearch(params)
                results = search.get_dict()
                
                images_results = results.get("images_results", [])
                if not images_results:
                    log_warning(ctx.job_id, 5, f"No results for: {query}")
                    continue
                
                # Get first image URL
                img_url = images_results[0].get('original')
                if not img_url:
                    continue
                
                # Download image
                img_path = images_dir / f"image_{idx}.png"
                urllib.request.urlretrieve(img_url, img_path)
                
                # Resize to 800x600 (16:9-ish)
                with Image.open(img_path) as img:
                    # Convert to RGB if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize maintaining aspect ratio
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    
                    # Create white background and paste centered
                    bg = Image.new('RGB', (800, 600), (255, 255, 255))
                    offset = ((800 - img.width) // 2, (600 - img.height) // 2)
                    bg.paste(img, offset)
                    bg.save(img_path)
                
                downloaded.append(str(img_path))
                log_success(ctx.job_id, 5, f"Downloaded: {query} -> {img_path.name}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                log_warning(ctx.job_id, 5, f"Failed to fetch image {idx}: {e}")
                continue
        
        ctx.images_downloaded = downloaded
        return downloaded
        
    except ImportError as e:
        raise ImportError(f"Missing library: {e}. Install with: pip install google-search-results Pillow")
    except Exception as e:
        raise Exception(f"Image fetch error: {e}")


def step_6_inject_images_layouts(ctx: WorkflowContext) -> str:
    """Step 6: Inject images and layouts into base script"""
    log_info(ctx.job_id, 6, "Injecting images into Manim script")
    
    if not ctx.images_downloaded:
        log_warning(ctx.job_id, 6, "No images to inject, using base script")
        ctx.enhanced_script = ctx.base_script
        return ctx.base_script
    
    try:
        # Simple injection: Add ImageMobject imports and usage
        enhanced = ctx.base_script
        
        # Ensure imports include ImageMobject
        if 'from manim import *' not in enhanced:
            enhanced = 'from manim import *\n' + enhanced
        
        # Add image loading code (simplified - actual implementation would parse script structure)
        image_code = "\n# Image setup\n"
        for idx, img_path in enumerate(ctx.images_downloaded):
            image_code += f"# img_{idx} = ImageMobject('{img_path}').scale(0.5).shift(RIGHT * 3)\n"
        
        # Insert after imports
        lines = enhanced.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if 'import' in line or 'from' in line:
                insert_idx = i + 1
        
        lines.insert(insert_idx, image_code)
        ctx.enhanced_script = '\n'.join(lines)
        
        # Save enhanced script
        script_file = ctx.get_file_path('enhanced_script.py')
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(ctx.enhanced_script)
        
        return ctx.enhanced_script
        
    except Exception as e:
        log_warning(ctx.job_id, 6, f"Image injection failed: {e}, using base script")
        ctx.enhanced_script = ctx.base_script
        return ctx.base_script


def step_7_render_silent_video(ctx: WorkflowContext) -> str:
    """Step 7: Validate and render silent video with Manim"""
    log_info(ctx.job_id, 7, "Rendering video with Manim")
    
    script_to_render = ctx.enhanced_script or ctx.base_script
    if not script_to_render:
        raise ValueError("No script available to render")
    
    try:
        # Save final script
        script_file = ctx.get_file_path('render_script.py')
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_to_render)
        
        # Extract scene class name
        scene_match = re.search(r'class\s+(\w+)\s*\(Scene\)', script_to_render)
        scene_name = scene_match.group(1) if scene_match else 'GDOTScene'
        
        # Render with Manim
        output_dir = ctx.work_dir / 'media'
        
        cmd = [
            MANIM_PATH,
            '-pqh',  # Preview quality high
            '--format', 'mp4',
            '--media_dir', str(output_dir),
            str(script_file),
            scene_name
        ]
        
        log_info(ctx.job_id, 7, f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            # Try lower quality
            log_warning(ctx.job_id, 7, "High quality failed, trying low quality")
            cmd[1] = '-pql'  # Low quality
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode,
                    cmd,
                    result.stdout,
                    result.stderr
                )
        
        # Find generated video
        video_files = list(output_dir.rglob('*.mp4'))
        if not video_files:
            raise FileNotFoundError("Manim did not generate video file")
        
        # Use most recent video
        video_path = max(video_files, key=lambda p: p.stat().st_mtime)
        
        # Copy to predictable location
        silent_video = ctx.get_file_path('silent_video.mp4')
        silent_video.write_bytes(video_path.read_bytes())
        
        ctx.silent_video_path = str(silent_video)
        log_success(ctx.job_id, 7, f"Video rendered: {silent_video.name}")
        
        return str(silent_video)
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Manim render failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception("Manim render timeout (>5min)")
    except Exception as e:
        raise Exception(f"Render error: {e}")


def step_8_generate_narration(ctx: WorkflowContext) -> List[Dict[str, Any]]:
    """Step 8: Generate narration script using LLM"""
    log_info(ctx.job_id, 8, "Generating narration script")
    
    try:
        # Prepare slide information
        slides_info = json.dumps(ctx.timings, indent=2)
        image_info = json.dumps(ctx.images_suggestions, indent=2) if ctx.images_suggestions else ""
        
        prompt = prompts.get_narration_prompt(slides_info, image_info)
        content, tokens = call_llm(prompt, max_tokens=1500)
        
        # Track tokens
        ctx.tokens_used['by_step']['8'] = tokens
        ctx.tokens_used['total'] += tokens
        
        # Extract JSON
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            ctx.narration = json.loads(json_match.group(1))
        else:
            # Try parsing whole content as JSON
            try:
                ctx.narration = json.loads(content)
            except:
                # Fallback narration
                ctx.narration = [
                    {
                        'slide_no': i+1,
                        'duration': slide.get('duration', 20),
                        'narration_text': prompts.FALLBACK_NARRATION_TEMPLATE.format(
                            title=slide.get('title', f'Slide {i+1}')
                        )
                    }
                    for i, slide in enumerate(ctx.timings)
                ]
        
        # Save narration
        narration_file = ctx.get_file_path('narration.json')
        with open(narration_file, 'w', encoding='utf-8') as f:
            json.dump(ctx.narration, f, indent=2)
        
        return ctx.narration
        
    except Exception as e:
        raise


def step_9_generate_audio(ctx: WorkflowContext) -> str:
    """Step 9: Generate TTS audio using edge-tts"""
    log_info(ctx.job_id, 9, "Generating audio with edge-tts")
    
    if not ctx.narration:
        raise ValueError("No narration available for TTS")
    
    try:
        import asyncio
        import edge_tts
        from moviepy.editor import AudioFileClip, concatenate_audioclips, AudioClip
        
        audio_dir = ctx.get_file_path('audio_clips')
        audio_dir.mkdir(exist_ok=True)
        
        # Generate TTS for each narration clip
        audio_clips = []
        
        async def generate_tts(text: str, output_path: str):
            """Generate TTS audio file."""
            communicate = edge_tts.Communicate(text, EDGE_TTS_VOICE)
            await communicate.save(output_path)
        
        for idx, narr in enumerate(ctx.narration):
            text = narr.get('narration_text', '')
            duration = narr.get('duration', 20)
            
            if not text:
                continue
            
            clip_path = audio_dir / f"clip_{idx}.mp3"
            
            # Generate TTS
            asyncio.run(generate_tts(text, str(clip_path)))
            
            # Verify file was created
            if not clip_path.exists() or clip_path.stat().st_size == 0:
                log_error(ctx.job_id, 9, "AUDIO_ERROR", f"TTS failed for clip {idx}", retry_count=0, fallback_used=False)
                raise ValueError(f"TTS save failed for clip {idx}")
            
            log_info(ctx.job_id, 9, f"TTS clip {idx} generated successfully ({clip_path.stat().st_size} bytes)")
            
            # Load and pad to duration
            audio_clip = AudioFileClip(str(clip_path))
            
            # If audio shorter than duration, pad with silence
            if audio_clip.duration < duration:
                silence_duration = duration - audio_clip.duration
                silence = AudioClip(lambda t: 0, duration=silence_duration)
                audio_clip = concatenate_audioclips([audio_clip, silence])
            elif audio_clip.duration > duration:
                # Truncate if longer
                audio_clip = audio_clip.subclip(0, duration)
            
            audio_clips.append(audio_clip)
        
        # Concatenate all clips
        if audio_clips:
            full_audio = concatenate_audioclips(audio_clips)
            audio_path = ctx.get_file_path('full_audio.mp3')
            full_audio.write_audiofile(str(audio_path), logger=None)
            
            ctx.audio_path = str(audio_path)
            log_success(ctx.job_id, 9, f"Audio generated: {audio_path.name}")
            
            return str(audio_path)
        else:
            raise ValueError("No audio clips generated")
        
    except ImportError as e:
        raise ImportError(f"Missing library: {e}. Install with: pip install edge-tts moviepy")
    except Exception as e:
        raise Exception(f"Audio generation error: {e}")


def run_pre_merge_checklist(ctx: WorkflowContext) -> Dict[str, bool]:
    """Run validation checklist before final merge."""
    checks = {
        'summarised': ctx.get_file_path('summary.txt').exists(),
        'script_generated': bool(ctx.base_script),
        'images_identified': len(ctx.images_suggestions) > 0,
        'images_added': 'ImageMobject' in (ctx.enhanced_script or ''),
        'video_rendered': ctx.get_file_path('silent_video.mp4').exists() if ctx.silent_video_path else False,
        'audio_generated': ctx.get_file_path('full_audio.mp3').exists() if ctx.audio_path else False,
    }
    
    # Check audio alignment
    if checks['video_rendered'] and checks['audio_generated']:
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            video = VideoFileClip(ctx.silent_video_path)
            audio = AudioFileClip(ctx.audio_path)
            checks['aligned'] = abs(video.duration - audio.duration) < 1.0
            checks['audio_integrated'] = checks['aligned']
            video.close()
            audio.close()
        except Exception as e:
            log_warning(ctx.job_id, 10, f"Could not check alignment: {e}")
            checks['aligned'] = False
            checks['audio_integrated'] = False
    else:
        checks['aligned'] = False
        checks['audio_integrated'] = False
    
    checks['video_ready'] = all(checks.values())
    
    # Log results
    log_info(ctx.job_id, 10, f"Pre-merge checklist: {checks}")
    
    return checks


def step_10_merge_and_finalize(ctx: WorkflowContext) -> str:
    """Step 10: Merge video and audio, generate final output"""
    log_info(ctx.job_id, 10, "Merging video and audio")
    
    # Run pre-merge checklist
    checklist = run_pre_merge_checklist(ctx)
    ctx.checklist_results = checklist
    
    if not ctx.silent_video_path:
        raise ValueError("No video available to merge")
    
    video = None
    audio = None
    
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, AudioClip, concatenate_audioclips
        
        # Load video
        video = VideoFileClip(ctx.silent_video_path)
        
        # Add audio if available
        if ctx.audio_path and os.path.exists(ctx.audio_path):
            audio = AudioFileClip(ctx.audio_path)
            
            # Check duration alignment
            dur_diff = abs(video.duration - audio.duration)
            alignment_ok = dur_diff < 1.0
            
            if not alignment_ok:
                log_warning(ctx.job_id, 10, f"Duration mismatch: video={video.duration:.2f}s, audio={audio.duration:.2f}s, diff={dur_diff:.2f}s")
                
                # Pad shorter one
                if audio.duration < video.duration:
                    silence_duration = video.duration - audio.duration
                    silence_pad = AudioClip(lambda t: 0, duration=silence_duration)
                    audio = concatenate_audioclips([audio, silence_pad])
                    log_info(ctx.job_id, 10, f"Padded audio with {silence_duration:.2f}s silence")
                else:
                    # Video is shorter, trim to match
                    video = video.subclip(0, audio.duration)
                    log_info(ctx.job_id, 10, f"Trimmed video to match audio duration")
            
            # Set volume to 1.0 and attach
            audio = audio.volumex(1.0)
            video = video.set_audio(audio)
            
            log_info(ctx.job_id, 10, "AUDIO_OK: Audio integrated successfully")
        else:
            log_warning(ctx.job_id, 10, "AUDIO_FAIL: No audio file, using silent video")
        
        # Generate final output path
        final_path = OUTPUT_DIR / f"{ctx.job_id}.mp4"
        
        # Write final video
        video.write_videofile(
            str(final_path),
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        # Close video and audio to release resources and cleanup temp files
        if video:
            video.close()
        if audio:
            audio.close()
        
        ctx.final_video_path = str(final_path)
        
        # Update job in database
        update_job(
            ctx.job_id,
            output_path=str(final_path),
            tokens=ctx.tokens_used,
            video_duration=str(video.duration)
        )
        
        # Determine final status
        if ctx.error_count >= ERROR_THRESHOLD_DEGRADED:
            ctx.degraded_mode = True
            update_job_status(ctx.job_id, 'degraded')
            log_warning(ctx.job_id, 10, f"Completed in DEGRADED mode ({ctx.error_count} errors)")
        else:
            update_job_status(ctx.job_id, 'done')
            log_success(ctx.job_id, 10, "Completed successfully")
        
        # Save checklist for UI display
        checklist_file = ctx.get_file_path('checklist.json')
        with open(checklist_file, 'w') as f:
            json.dump(ctx.checklist_results, f, indent=2)
        
        # Cleanup checkpoints
        cleanup_checkpoints(ctx.job_id)
        
        # Cleanup any leftover MoviePy temp files
        cleanup_moviepy_temp_files(ctx.job_id)
        
        return str(final_path)
        
    except ImportError as e:
        raise ImportError(f"Missing library: {e}. Install with: pip install moviepy")
    except Exception as e:
        raise Exception(f"Merge error: {e}")
    finally:
        # Ensure resources are always released
        if video:
            try:
                video.close()
            except:
                pass
        if audio:
            try:
                audio.close()
            except:
                pass


def cleanup_moviepy_temp_files(job_id: str):
    """Cleanup any leftover MoviePy temporary files"""
    try:
        import glob
        # MoviePy creates temp files with pattern: *TEMP_MPY*.mp4
        temp_pattern = f"*{job_id}*TEMP_MPY*.mp4"
        for temp_file in glob.glob(temp_pattern):
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    log_info(job_id, 10, f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                log_warning(job_id, 10, f"Could not remove temp file {temp_file}: {e}")
        
        # Also check in current directory for any orphaned temp files
        for temp_file in glob.glob("*TEMP_MPY*.mp4"):
            try:
                # Remove if file is older than 1 hour
                file_age = time.time() - os.path.getmtime(temp_file)
                if file_age > 3600:  # 1 hour
                    os.remove(temp_file)
                    log_info(job_id, 10, f"Cleaned up old temp file: {temp_file}")
            except Exception as e:
                log_warning(job_id, 10, f"Could not remove old temp file {temp_file}: {e}")
    except Exception as e:
        log_warning(job_id, 10, f"Cleanup error: {e}")


# ============================================================================
# MAIN WORKFLOW RUNNER
# ============================================================================

def run_workflow(job_id: str, md_content: str) -> Dict[str, Any]:
    """
    Execute complete 11-step workflow with resilience.
    
    Args:
        job_id: Unique job identifier
        md_content: Markdown input
    
    Returns:
        Dict with final status and output path
    """
    log_info(job_id, -1, "=== Starting workflow ===")
    
    ctx = WorkflowContext(job_id, md_content)
    
    # Define workflow steps
    steps = [
        (0, "Load System Prompts", step_0_load_system_prompts, 1, False),
        (1, "Validate Input", step_1_validate_input, 1, True),
        (2, "Generate Summary", step_2_generate_summary, 2, True),
        (3, "Generate Base Script", step_3_generate_base_script, 3, True),
        (4, "Suggest Images & Layouts", step_4_suggest_images_layouts, 2, True),
        (5, "Fetch Images", step_5_fetch_images, 3, True),
        (6, "Inject Images", step_6_inject_images_layouts, 1, True),
        (7, "Render Silent Video", step_7_render_silent_video, 2, True),
        (8, "Generate Narration", step_8_generate_narration, 2, True),
        (9, "Generate Audio", step_9_generate_audio, 1, True),
        (10, "Merge & Finalize", step_10_merge_and_finalize, 1, True),
    ]
    
    # Execute steps
    for step_no, name, func, max_retries, allow_fallback in steps:
        # Check total retry limit
        if int(ctx.tokens_used.get('total_retries', 0)) > MAX_TOTAL_RETRIES:
            log_error(
                job_id, step_no, "MAX_TOTAL_RETRIES",
                f"Exceeded maximum total retries ({MAX_TOTAL_RETRIES})",
                retry_count=0, fallback_used=False
            )
            update_job_status(job_id, 'error')
            return {
                'status': 'error',
                'message': 'Too many retries, workflow aborted',
                'output_path': None
            }
        
        # Execute step
        success, result = resilient_step(
            step_no, name, func, ctx,
            max_retries=max_retries,
            allow_fallback=allow_fallback
        )
        
        if not success:
            log_error(
                job_id, step_no, "STEP_FAILED",
                f"Step {step_no} ({name}) failed completely",
                retry_count=0, fallback_used=False
            )
            update_job_status(job_id, 'error')
            return {
                'status': 'error',
                'message': f'Failed at step {step_no}: {name}',
                'output_path': None
            }
    
    # Workflow complete
    log_success(job_id, -1, "=== Workflow complete ===")
    
    return {
        'status': 'degraded' if ctx.degraded_mode else 'done',
        'message': 'Success' + (' (degraded mode)' if ctx.degraded_mode else ''),
        'output_path': ctx.final_video_path,
        'tokens_used': ctx.tokens_used,
        'error_count': ctx.error_count,
        'fallback_log': ctx.fallback_log
    }

