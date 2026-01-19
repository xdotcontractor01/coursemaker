================================================================================
GDOT VIDEO GENERATION - TEST WORKFLOW SCRIPTS
================================================================================

This folder contains 11 individual workflow step scripts for easy testing,
debugging, and understanding of the video generation pipeline.

FOLDER STRUCTURE:
--------------------------------------------------------------------------------
test_workflow/
├── shared.py                    # Common utilities and configuration
├── step_00_load_prompts.py      # Load system prompts
├── step_01_validate_input.py    # Validate markdown input
├── step_02_generate_summary.py  # Generate content summary
├── step_03_generate_base_script.py  # Generate Manim script
├── step_04_suggest_images.py    # Suggest images for slides
├── step_05_download_images.py   # Download images via SerpAPI
├── step_06_inject_images.py     # Inject images into script
├── step_07_render_video.py      # Render video with Manim
├── step_08_generate_narration.py # Generate narration text
├── step_09_generate_audio.py    # Generate audio clips
├── step_10_merge_audio_video.py # Merge audio with video
└── run_all.py                   # Run all steps sequentially

OUTPUT DIRECTORY:
--------------------------------------------------------------------------------
All outputs are saved to: test_output/

USAGE:
--------------------------------------------------------------------------------

1. RUN COMPLETE WORKFLOW:
   cd test_workflow
   python run_all.py

   This runs all 11 steps and displays a comprehensive quality report.

2. RUN INDIVIDUAL STEPS:
   cd test_workflow
   python step_00_load_prompts.py
   python step_01_validate_input.py
   python step_02_generate_summary.py
   ... and so on

3. CUSTOM INPUT:
   python step_01_validate_input.py path/to/your/input.md

   If no file is provided, the sample content from shared.py is used.

4. RERUN SPECIFIC STEP:
   If step 7 (render) fails, you can fix the script and rerun:
   python step_07_render_video.py

   Each step reads its required inputs from test_output/ so you can
   run any step independently as long as previous steps completed.

DEPENDENCIES:
--------------------------------------------------------------------------------
Required:
- openai
- python-dotenv
- manim

Optional (for images):
- SERPAPI_KEY environment variable
- requests

Optional (for audio):
- edge-tts
- moviepy

ENVIRONMENT VARIABLES:
--------------------------------------------------------------------------------
Required:
- OPENAI_API_KEY: Your OpenAI API key

Optional:
- SERPAPI_KEY: Your SerpAPI key (for image downloads)

Set in .env file in project root.

TROUBLESHOOTING:
--------------------------------------------------------------------------------

1. If a step fails:
   - Check the error message
   - Verify previous step outputs exist in test_output/
   - Run the step again to see detailed error logs

2. Common issues:
   - Missing API keys: Check .env file
   - Syntax errors in script: Check test_output/base_script.py
   - Manim render failures: Check if manim is installed correctly
   - Audio generation fails: Install edge-tts

3. Debugging tips:
   - Each step is self-contained and can be run independently
   - Check test_output/ folder for intermediate files
   - Read the step script source code for details
   - Token usage is saved in tokens_step_XX.txt files

WORKFLOW STEPS EXPLAINED:
--------------------------------------------------------------------------------

Step 0: Load system prompts
  - Saves SYSTEM_GDOT prompt to file
  - No dependencies

Step 1: Validate input
  - Validates markdown content
  - Saves to input.md
  - Depends on: none

Step 2: Generate summary
  - Calls LLM to create 100-word summary
  - Depends on: step 1 (input.md)

Step 3: Generate base script
  - Calls LLM to create Manim script with visual elements
  - Validates syntax and checks for shapes
  - Depends on: step 2 (summary.txt)

Step 4: Suggest images
  - Calls LLM to suggest images for slides
  - Depends on: steps 2, 3 (summary.txt, timings.json)

Step 5: Download images
  - Downloads images from SerpAPI
  - Depends on: step 4 (images.json)

Step 6: Inject images
  - Injects ImageMobject code into script
  - Uses LayoutManager for positioning
  - Depends on: steps 3, 5 (base_script.py, downloaded images)

Step 7: Render video
  - Runs Manim to create video
  - Depends on: step 6 (render_script.py)

Step 8: Generate narration
  - Calls LLM to create detailed narration
  - Depends on: steps 2, 3 (summary.txt, timings.json)

Step 9: Generate audio
  - Uses edge-tts to create audio clips
  - Depends on: step 8 (narration.json)

Step 10: Merge audio & video
  - Uses moviepy to combine audio and video
  - Depends on: steps 7, 9 (video, audio clips)

QUALITY REPORT:
--------------------------------------------------------------------------------
run_all.py displays a comprehensive quality report including:
- Visual element counts (shapes, text, images)
- Quality assessment (excellent/good/fair/poor)
- Audio generation status
- Final video location and size
- Total tokens used

TIPS:
--------------------------------------------------------------------------------
1. Run complete workflow first to see baseline results
2. If quality is poor, regenerate step 3 with more emphasis on visuals
3. Edit generated scripts manually if needed, then continue from step 7
4. Use individual steps for quick iteration on specific parts
5. Check token usage to optimize costs

================================================================================













