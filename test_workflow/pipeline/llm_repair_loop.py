"""
LLM Repair Loop Module
Auto-fixes failing Manim scripts using LLM with up to 3 iterations.
Generates failure_ticket.json if repair fails after max attempts.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import call_llm, print_info, print_success, print_error

from .dry_run_validator import (
    DryRunValidator,
    ValidationResult,
    ValidationError,
    validate_script
)


@dataclass
class RepairAttempt:
    """Record of a single repair attempt"""
    attempt_number: int
    error_type: str
    error_message: str
    context: Optional[str]
    fix_applied: str
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RepairResult:
    """Result of the repair loop"""
    video_id: str
    script_path: Path
    original_errors: List[ValidationError]
    repair_attempts: List[RepairAttempt]
    final_success: bool
    final_script: str
    failure_ticket_path: Optional[Path] = None


class LLMRepairLoop:
    """Auto-repairs Manim scripts using LLM"""
    
    MAX_ATTEMPTS = 3
    CONTEXT_LINES = 20  # Lines of context around error
    
    REPAIR_PROMPT = """You are an expert Manim debugger. Fix the following error in this Manim script.

═══════════════════════════════════════════════════════════════════════════════
ERROR INFORMATION
═══════════════════════════════════════════════════════════════════════════════

Error Type: {error_type}
Error Message: {error_message}
Line Number: {line_number}

═══════════════════════════════════════════════════════════════════════════════
CODE CONTEXT (around error)
═══════════════════════════════════════════════════════════════════════════════

{context}

═══════════════════════════════════════════════════════════════════════════════
FULL SCRIPT
═══════════════════════════════════════════════════════════════════════════════

{full_script}

═══════════════════════════════════════════════════════════════════════════════
COMMON FIXES
═══════════════════════════════════════════════════════════════════════════════

1. IndexError: Check list/array access - ensure index exists
2. NameError: Check variable is defined before use
3. AttributeError: Check object has the method/property
4. TypeError: Check argument types match function signature
5. SyntaxError: Check indentation, colons, parentheses
6. Diversity errors: Add more animation types or shapes

═══════════════════════════════════════════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

1. Identify the exact cause of the error
2. Fix ONLY what's necessary - don't rewrite the whole script
3. Ensure the fix maintains the visual intent of the slide
4. If a diversity error, add appropriate animations/shapes

Return ONLY the complete fixed Python script (no markdown, no explanation).
Start your response with: from manim import *
"""

    DIVERSITY_FIX_PROMPT = """You are an expert Manim animator. This script lacks visual diversity.

═══════════════════════════════════════════════════════════════════════════════
DIVERSITY ISSUES
═══════════════════════════════════════════════════════════════════════════════

{diversity_issues}

═══════════════════════════════════════════════════════════════════════════════
CURRENT SCRIPT
═══════════════════════════════════════════════════════════════════════════════

{full_script}

═══════════════════════════════════════════════════════════════════════════════
REQUIRED ADDITIONS
═══════════════════════════════════════════════════════════════════════════════

To fix diversity issues, add:

1. Dynamic elements (at least one):
   - MoveAlongPath: tracer moving along a path
   - ValueTracker: animated number changes
   - self.camera.frame.animate: zoom/pan effects

2. Animation variety (per slide, at least 2 types):
   - Write, Create, FadeIn, FadeOut
   - GrowFromCenter, GrowFromEdge
   - Transform, ReplacementTransform
   - Indicate, Circumscribe, Flash

3. Shape variety:
   - Use Circles, Arrows, Lines, not just Rectangles
   - Add visual interest with Braces, NumberLines

4. Color variety:
   - Use BLUE, ORANGE, GREEN, RED, GOLD, TEAL

═══════════════════════════════════════════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

Enhance the script by adding the required diversity elements.
Keep the original content/message but make it more visually engaging.

Return ONLY the complete enhanced Python script (no markdown, no explanation).
Start your response with: from manim import *
"""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir
        self.validator = DryRunValidator(output_dir)
    
    def repair_script(
        self,
        script_path: Path,
        video_id: str = "",
        initial_validation: Optional[ValidationResult] = None
    ) -> RepairResult:
        """Attempt to repair a failing script with up to MAX_ATTEMPTS iterations"""
        
        if not video_id:
            video_id = script_path.stem
        
        # Initial validation if not provided
        if initial_validation is None:
            initial_validation = self.validator.validate_script(script_path, video_id)
        
        if initial_validation.passed:
            print_success("Script already passes validation - no repair needed")
            return RepairResult(
                video_id=video_id,
                script_path=script_path,
                original_errors=[],
                repair_attempts=[],
                final_success=True,
                final_script=script_path.read_text()
            )
        
        original_errors = initial_validation.errors.copy()
        repair_attempts = []
        current_script = script_path.read_text()
        
        print_info(f"Starting repair loop for {video_id} ({len(original_errors)} errors)")
        
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            print_info(f"\n--- Repair Attempt {attempt}/{self.MAX_ATTEMPTS} ---")
            
            # Get the first unresolved error
            validation = self.validator.validate_script(script_path, video_id)
            if validation.passed:
                print_success(f"Script repaired after {attempt - 1} attempts!")
                return RepairResult(
                    video_id=video_id,
                    script_path=script_path,
                    original_errors=original_errors,
                    repair_attempts=repair_attempts,
                    final_success=True,
                    final_script=current_script
                )
            
            error = validation.errors[0]  # Focus on first error
            
            # Generate fix
            fixed_script = self._generate_fix(
                current_script,
                error,
                is_diversity_error=(error.error_type == "diversity")
            )
            
            if fixed_script:
                # Save the fixed script
                script_path.write_text(fixed_script, encoding='utf-8')
                current_script = fixed_script
                
                # Validate the fix
                new_validation = self.validator.validate_script(script_path, video_id)
                success = new_validation.passed or len(new_validation.errors) < len(validation.errors)
                
                repair_attempts.append(RepairAttempt(
                    attempt_number=attempt,
                    error_type=error.error_type,
                    error_message=error.message,
                    context=error.context,
                    fix_applied=f"LLM repair for {error.error_type} error",
                    success=success
                ))
                
                if success:
                    print_success(f"Fix improved the script (errors: {len(validation.errors)} -> {len(new_validation.errors)})")
                else:
                    print_error("Fix did not improve the script")
            else:
                repair_attempts.append(RepairAttempt(
                    attempt_number=attempt,
                    error_type=error.error_type,
                    error_message=error.message,
                    context=error.context,
                    fix_applied="LLM failed to generate fix",
                    success=False
                ))
        
        # Final validation
        final_validation = self.validator.validate_script(script_path, video_id)
        final_success = final_validation.passed
        
        result = RepairResult(
            video_id=video_id,
            script_path=script_path,
            original_errors=original_errors,
            repair_attempts=repair_attempts,
            final_success=final_success,
            final_script=current_script
        )
        
        if not final_success:
            # Generate failure ticket
            print_error(f"Repair failed after {self.MAX_ATTEMPTS} attempts")
            result.failure_ticket_path = self._generate_failure_ticket(result, final_validation)
        
        return result
    
    def _generate_fix(
        self,
        script: str,
        error: ValidationError,
        is_diversity_error: bool = False
    ) -> Optional[str]:
        """Generate a fix for the given error using LLM"""
        
        # Build context
        context = error.context
        if not context and error.line_number:
            lines = script.split('\n')
            start = max(0, error.line_number - self.CONTEXT_LINES // 2)
            end = min(len(lines), error.line_number + self.CONTEXT_LINES // 2)
            context = '\n'.join(f"{i+1:4d}: {lines[i]}" for i in range(start, end))
        
        # Choose prompt
        if is_diversity_error:
            # Collect all diversity issues
            validator = DryRunValidator()
            diversity_errors, diversity_score = validator._check_diversity(script)
            diversity_issues = "\n".join(f"- {e.message}" for e in diversity_errors if e)
            
            prompt = self.DIVERSITY_FIX_PROMPT.format(
                diversity_issues=diversity_issues or error.message,
                full_script=script[:8000]  # Limit length
            )
        else:
            prompt = self.REPAIR_PROMPT.format(
                error_type=error.error_type,
                error_message=error.message,
                line_number=error.line_number or "unknown",
                context=context or "Not available",
                full_script=script[:8000]
            )
        
        try:
            print_info(f"Calling LLM for {error.error_type} fix...")
            response, tokens = call_llm(prompt, max_tokens=5000, temperature=0.3)
            print_info(f"LLM tokens used: {tokens}")
            
            # Clean up response
            fixed_script = response.strip()
            
            # Remove markdown if present
            if fixed_script.startswith("```"):
                fixed_script = re.sub(r'^```\w*\n?', '', fixed_script)
                fixed_script = re.sub(r'\n?```$', '', fixed_script)
            
            # Ensure it starts with imports
            if not fixed_script.startswith("from manim"):
                # Try to find where the actual script starts
                match = re.search(r'from manim import', fixed_script)
                if match:
                    fixed_script = fixed_script[match.start():]
                else:
                    print_error("LLM response doesn't contain valid manim script")
                    return None
            
            # Basic validation
            try:
                compile(fixed_script, '<string>', 'exec')
            except SyntaxError as e:
                print_error(f"LLM generated invalid syntax: {e}")
                return None
            
            return fixed_script
            
        except Exception as e:
            print_error(f"LLM repair failed: {e}")
            return None
    
    def _generate_failure_ticket(
        self,
        result: RepairResult,
        final_validation: ValidationResult
    ) -> Path:
        """Generate a failure ticket for manual intervention"""
        
        ticket = {
            "video_id": result.video_id,
            "script_path": str(result.script_path),
            "created_at": datetime.now().isoformat(),
            "status": "requires_manual_fix",
            "original_errors": [
                {
                    "type": e.error_type,
                    "message": e.message,
                    "line": e.line_number,
                    "suggestion": e.suggestion
                }
                for e in result.original_errors
            ],
            "repair_attempts": [
                {
                    "attempt": a.attempt_number,
                    "error_type": a.error_type,
                    "fix_applied": a.fix_applied,
                    "success": a.success
                }
                for a in result.repair_attempts
            ],
            "remaining_errors": [
                {
                    "type": e.error_type,
                    "message": e.message,
                    "line": e.line_number,
                    "context": e.context,
                    "suggestion": e.suggestion
                }
                for e in final_validation.errors
            ],
            "manual_checklist": [
                "Review the error messages and context",
                "Check for common issues: list indices, variable names, method calls",
                "Verify manim animation syntax",
                "Ensure visual diversity requirements are met",
                "Run: python dry_run_validator.py <script_path> to test fixes"
            ]
        }
        
        ticket_path = result.script_path.parent / f"failure_ticket_{result.video_id}.json"
        ticket_path.write_text(json.dumps(ticket, indent=2))
        
        print_error(f"Failure ticket created: {ticket_path}")
        
        return ticket_path
    
    def save_repair_history(self, result: RepairResult) -> Path:
        """Save repair history to JSON"""
        history = {
            "video_id": result.video_id,
            "script_path": str(result.script_path),
            "original_error_count": len(result.original_errors),
            "repair_attempts": len(result.repair_attempts),
            "final_success": result.final_success,
            "failure_ticket": str(result.failure_ticket_path) if result.failure_ticket_path else None,
            "attempts": [
                {
                    "number": a.attempt_number,
                    "error_type": a.error_type,
                    "error_message": a.error_message[:200],
                    "fix_applied": a.fix_applied,
                    "success": a.success,
                    "timestamp": a.timestamp
                }
                for a in result.repair_attempts
            ]
        }
        
        history_path = result.script_path.parent / "repair_history.json"
        history_path.write_text(json.dumps(history, indent=2))
        
        return history_path


def repair_script(script_path: Path, video_id: str = "") -> RepairResult:
    """Convenience function to repair a script"""
    repairer = LLMRepairLoop()
    return repairer.repair_script(script_path, video_id)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python llm_repair_loop.py <script_path>")
        sys.exit(1)
    
    script_path = Path(sys.argv[1])
    
    print(f"\nRepairing: {script_path}")
    print("="*60)
    
    repairer = LLMRepairLoop()
    result = repairer.repair_script(script_path)
    
    print("\n" + "="*60)
    print("REPAIR RESULT")
    print("="*60)
    print(f"Success: {'[YES]' if result.final_success else '[NO]'}")
    print(f"Original errors: {len(result.original_errors)}")
    print(f"Repair attempts: {len(result.repair_attempts)}")
    
    if result.failure_ticket_path:
        print(f"Failure ticket: {result.failure_ticket_path}")
    
    # Save history
    history_path = repairer.save_repair_history(result)
    print(f"History saved: {history_path}")

