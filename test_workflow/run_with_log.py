"""Run workflow with logging to file"""
import sys
import os

# Change to the test_workflow directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Redirect output to log file
log_file = open('workflow_log.txt', 'w', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

try:
    # Import and run each step
    print("=" * 80)
    print("STARTING WORKFLOW")
    print("=" * 80)
    
    import step_02_generate_summary
    step_02_generate_summary.main()
    
    import step_03_generate_base_script
    step_03_generate_base_script.main()
    
    import step_04_suggest_images
    step_04_suggest_images.main()
    
    import step_05_download_images
    step_05_download_images.main()
    
    import step_06_inject_images
    step_06_inject_images.main()
    
    import step_07_render_video
    step_07_render_video.main()
    
    import step_08_generate_narration
    step_08_generate_narration.main()
    
    import step_09_generate_audio
    step_09_generate_audio.main()
    
    import step_10_merge_audio_video
    step_10_merge_audio_video.main()
    
    print("=" * 80)
    print("WORKFLOW COMPLETE!")
    print("=" * 80)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    log_file.close()
    
# Print to console that we're done
sys.stdout = sys.__stdout__
print("Workflow completed! Check workflow_log.txt for details.")








