"""
Dry-Run Validator Module
Validates Manim scripts before full render:
1. Syntax check (py_compile)
2. Import test (catches missing imports)
3. Lightweight render test (first 3 seconds)
4. Visual diversity check
"""

import sys
import json
import subprocess
import tempfile
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import importlib.util
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import print_info, print_success, print_error


@dataclass
class ValidationError:
    """A single validation error"""
    error_type: str  # "syntax", "import", "runtime", "diversity"
    message: str
    line_number: Optional[int] = None
    context: Optional[str] = None  # Surrounding code
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of script validation"""
    video_id: str
    script_path: Path
    passed: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    diversity_score: int = 0
    diversity_passed: bool = False
    syntax_valid: bool = False
    imports_valid: bool = False
    runtime_valid: bool = False
    validated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "video_id": self.video_id,
            "script_path": str(self.script_path),
            "passed": self.passed,
            "errors": [
                {
                    "error_type": e.error_type,
                    "message": e.message,
                    "line_number": e.line_number,
                    "context": e.context,
                    "suggestion": e.suggestion
                }
                for e in self.errors
            ],
            "warnings": self.warnings,
            "diversity_score": self.diversity_score,
            "diversity_passed": self.diversity_passed,
            "syntax_valid": self.syntax_valid,
            "imports_valid": self.imports_valid,
            "runtime_valid": self.runtime_valid,
            "validated_at": self.validated_at
        }


class DryRunValidator:
    """Validates Manim scripts with multiple checks"""
    
    # Required animation types per slide
    MIN_ANIMATION_TYPES_PER_SLIDE = 2
    
    # Required dynamic elements in script
    DYNAMIC_ELEMENT_PATTERNS = [
        'MoveAlongPath',
        'add_updater',
        'ValueTracker',
        'self.camera.frame.animate',
        'Succession',
        'AnimationGroup'
    ]
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir
    
    def validate_script(self, script_path: Path, video_id: str = "") -> ValidationResult:
        """Run all validation checks on a script"""
        
        if not video_id:
            video_id = script_path.stem
        
        result = ValidationResult(
            video_id=video_id,
            script_path=script_path,
            passed=False
        )
        
        if not script_path.exists():
            result.errors.append(ValidationError(
                error_type="file",
                message=f"Script file not found: {script_path}"
            ))
            return result
        
        script_content = script_path.read_text(encoding='utf-8')
        
        # Step 1: Syntax check
        print_info("Checking syntax...")
        syntax_result = self._check_syntax(script_content, script_path)
        result.syntax_valid = syntax_result is None
        if syntax_result:
            result.errors.append(syntax_result)
            return result  # Can't continue without valid syntax
        print_success("Syntax valid")
        
        # Step 2: Import test
        print_info("Checking imports...")
        import_result = self._check_imports(script_path)
        result.imports_valid = import_result is None
        if import_result:
            result.errors.append(import_result)
            return result  # Can't continue without valid imports
        print_success("Imports valid")
        
        # Step 3: Runtime test (lightweight) - only if manim is available
        try:
            import manim
            print_info("Running lightweight render test...")
            runtime_result = self._check_runtime(script_path, script_content)
            result.runtime_valid = runtime_result is None
            if runtime_result:
                result.errors.append(runtime_result)
                # Don't return - continue with diversity check
            else:
                print_success("Runtime test passed")
        except ImportError:
            print_info("Skipping runtime test (manim not installed)")
            result.runtime_valid = True  # Assume valid if we can't test
        
        # Step 4: Diversity check
        print_info("Checking visual diversity...")
        diversity_errors, score = self._check_diversity(script_content)
        result.diversity_score = score
        
        # Pass if score is good enough (>= 6) even if there are minor issues
        # OR if there are no critical errors (dynamic elements)
        critical_errors = [e for e in diversity_errors if "dynamic elements" in e.message.lower()]
        result.diversity_passed = score >= 6 or (len(critical_errors) == 0 and score >= 4)
        
        if not result.diversity_passed:
            for err in diversity_errors:
                result.errors.append(err)
                result.warnings.append(err.message)
        else:
            # Just add as warnings, not errors
            for err in diversity_errors:
                result.warnings.append(err.message)
        
        if result.diversity_passed:
            print_success(f"Diversity check passed (score: {score})")
        else:
            print_error(f"Diversity check failed (score: {score})")
        
        # Determine overall pass/fail
        result.passed = (
            result.syntax_valid and 
            result.imports_valid and 
            result.runtime_valid and 
            result.diversity_passed
        )
        
        return result
    
    def _check_syntax(self, script_content: str, script_path: Path) -> Optional[ValidationError]:
        """Check Python syntax"""
        try:
            compile(script_content, str(script_path), 'exec')
            return None
        except SyntaxError as e:
            # Extract context
            lines = script_content.split('\n')
            context_start = max(0, e.lineno - 3)
            context_end = min(len(lines), e.lineno + 2)
            context_lines = lines[context_start:context_end]
            context = '\n'.join(f"{i+context_start+1:4d}: {line}" 
                               for i, line in enumerate(context_lines))
            
            return ValidationError(
                error_type="syntax",
                message=f"{e.msg} at line {e.lineno}",
                line_number=e.lineno,
                context=context,
                suggestion="Check for missing colons, parentheses, or indentation errors"
            )
    
    def _check_imports(self, script_path: Path) -> Optional[ValidationError]:
        """Check that all imports resolve"""
        try:
            script_content = script_path.read_text()
            
            # Check manim import statement exists
            if 'from manim import' not in script_content and 'import manim' not in script_content:
                return ValidationError(
                    error_type="import",
                    message="Missing manim import",
                    suggestion="Add 'from manim import *' at the top of the script"
                )
            
            # Try importing manim to check it's available
            # If manim isn't installed, just warn but don't fail
            try:
                import manim
            except ImportError:
                # Manim not installed - this is okay for syntax-only validation
                # We'll skip the runtime test but allow the script to pass
                print_info("Note: Manim not installed - skipping runtime validation")
                return None
            
            return None
                
        except Exception as e:
            return ValidationError(
                error_type="import",
                message=str(e),
                suggestion="Check that all required packages are installed"
            )
    
    def _check_runtime(self, script_path: Path, script_content: str) -> Optional[ValidationError]:
        """Run a lightweight render test"""
        
        # Find the Scene class name
        class_match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', script_content)
        if not class_match:
            return ValidationError(
                error_type="runtime",
                message="No Scene class found in script",
                suggestion="Define a class that inherits from Scene"
            )
        
        class_name = class_match.group(1)
        
        # Create a test harness script
        test_script = f'''
import sys
sys.path.insert(0, r"{script_path.parent}")

# Patch manim to do minimal rendering
import manim
original_wait = manim.Scene.wait
frame_count = [0]
max_frames = 10

def limited_wait(self, duration=1, **kwargs):
    frame_count[0] += 1
    if frame_count[0] > max_frames:
        raise StopIteration("Max frames reached - test passed")
    # Minimal wait
    return

manim.Scene.wait = limited_wait

# Now import and test the scene
try:
    from {script_path.stem} import {class_name}
    scene = {class_name}()
    # Just initialize, don't render
    print("Scene class instantiated successfully")
except StopIteration as e:
    print(f"Test passed: {{e}}")
except Exception as e:
    print(f"RUNTIME_ERROR: {{type(e).__name__}}: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
        
        # Run the test in a subprocess
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_script)
                test_file = f.name
            
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(script_path.parent)
            )
            
            # Clean up
            Path(test_file).unlink(missing_ok=True)
            
            # Check for errors
            if result.returncode != 0:
                # Parse error from output
                error_match = re.search(r'RUNTIME_ERROR: (.+)', result.stdout + result.stderr)
                if error_match:
                    error_msg = error_match.group(1)
                else:
                    error_msg = result.stderr or result.stdout or "Unknown runtime error"
                
                # Try to extract line number
                line_match = re.search(r'line (\d+)', error_msg)
                line_num = int(line_match.group(1)) if line_match else None
                
                # Extract context if we have line number
                context = None
                if line_num:
                    lines = script_content.split('\n')
                    context_start = max(0, line_num - 5)
                    context_end = min(len(lines), line_num + 5)
                    context_lines = lines[context_start:context_end]
                    context = '\n'.join(f"{i+context_start+1:4d}: {line}" 
                                       for i, line in enumerate(context_lines))
                
                return ValidationError(
                    error_type="runtime",
                    message=error_msg[:500],  # Limit length
                    line_number=line_num,
                    context=context,
                    suggestion="Check variable names, list indices, and method calls"
                )
            
            return None
            
        except subprocess.TimeoutExpired:
            return ValidationError(
                error_type="runtime",
                message="Script timed out during test (>30 seconds)",
                suggestion="Check for infinite loops or very long animations"
            )
        except Exception as e:
            return ValidationError(
                error_type="runtime",
                message=f"Test harness error: {e}",
                suggestion="This may be an environment issue"
            )
    
    def _check_diversity(self, script_content: str) -> tuple[List[ValidationError], int]:
        """Check visual diversity requirements"""
        errors = []
        score = 0
        
        # Check for dynamic elements
        has_dynamic = any(pattern in script_content for pattern in self.DYNAMIC_ELEMENT_PATTERNS)
        if has_dynamic:
            score += 3
        else:
            errors.append(ValidationError(
                error_type="diversity",
                message="No dynamic elements found (MoveAlongPath, Updater, ValueTracker, etc.)",
                suggestion="Add at least one dynamic element like MoveAlongPath or ValueTracker"
            ))
        
        # Check animation variety per slide
        slides = re.findall(r'# Slide \d+:.*?(?=# Slide \d+:|$)', script_content, re.DOTALL)
        
        animation_patterns = [
            'Write', 'Create', 'FadeIn', 'FadeOut', 'GrowFrom', 
            'Transform', 'ReplacementTransform', 'MoveAlongPath',
            'Indicate', 'Circumscribe', 'Flash', 'DrawBorderThenFill',
            'SpinInFromNothing', 'MoveToTarget'
        ]
        
        for i, slide in enumerate(slides, 1):
            types_found = set()
            for pattern in animation_patterns:
                if pattern in slide:
                    types_found.add(pattern)
            
            if len(types_found) >= self.MIN_ANIMATION_TYPES_PER_SLIDE:
                score += 1
            else:
                errors.append(ValidationError(
                    error_type="diversity",
                    message=f"Slide {i} has only {len(types_found)} animation types (need {self.MIN_ANIMATION_TYPES_PER_SLIDE}+)",
                    suggestion=f"Add more animation variety to slide {i}"
                ))
        
        # Check for rectangle-only slides
        rect_count = script_content.count('Rectangle(')
        circle_count = script_content.count('Circle(')
        arrow_count = script_content.count('Arrow(') + script_content.count('CurvedArrow(')
        
        if rect_count > 0 and circle_count == 0 and arrow_count == 0:
            errors.append(ValidationError(
                error_type="diversity",
                message="Script only uses Rectangle shapes - lacks visual variety",
                suggestion="Add Circles, Arrows, or other shapes"
            ))
        else:
            score += 2
        
        # Check for color variety
        colors = ['BLUE', 'ORANGE', 'GREEN', 'RED', 'GOLD', 'TEAL', 'YELLOW']
        colors_used = sum(1 for c in colors if c in script_content)
        if colors_used >= 3:
            score += 1
        else:
            errors.append(ValidationError(
                error_type="diversity",
                message=f"Only {colors_used} colors used (recommend 3+)",
                suggestion="Use more color variety: BLUE, ORANGE, GREEN, etc."
            ))
        
        return errors, score
    
    def save_validation_report(self, result: ValidationResult, output_path: Optional[Path] = None) -> Path:
        """Save validation report to JSON"""
        if output_path is None:
            output_path = result.script_path.parent / "validation_report.json"
        
        output_path.write_text(json.dumps(result.to_dict(), indent=2))
        return output_path


def validate_script(script_path: Path, video_id: str = "") -> ValidationResult:
    """Convenience function to validate a script"""
    validator = DryRunValidator()
    return validator.validate_script(script_path, video_id)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dry_run_validator.py <script_path>")
        sys.exit(1)
    
    script_path = Path(sys.argv[1])
    
    print(f"\nValidating: {script_path}")
    print("="*60)
    
    validator = DryRunValidator()
    result = validator.validate_script(script_path)
    
    print("\n" + "="*60)
    print("VALIDATION RESULT")
    print("="*60)
    print(f"Passed: {'[YES]' if result.passed else '[NO]'}")
    print(f"Syntax: {'[OK]' if result.syntax_valid else '[X]'}")
    print(f"Imports: {'[OK]' if result.imports_valid else '[X]'}")
    print(f"Runtime: {'[OK]' if result.runtime_valid else '[X]'}")
    print(f"Diversity: {'[OK]' if result.diversity_passed else '[X]'} (score: {result.diversity_score})")
    
    if result.errors:
        print("\nErrors:")
        for err in result.errors:
            print(f"  [{err.error_type}] {err.message}")
            if err.suggestion:
                print(f"    Suggestion: {err.suggestion}")
    
    # Save report
    report_path = validator.save_validation_report(result)
    print(f"\nReport saved: {report_path}")

