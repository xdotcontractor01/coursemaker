"""
Step 10: Merge Audio & Video
Merges audio clips with video using moviepy
"""

import json
from shared import *

def main():
    """Merge audio clips and sync with video"""
    print_step(10, "Merge Audio & Video")
    
    # Try moviepy 2.x imports first, fallback to 1.x
    try:
        from moviepy import VideoFileClip, AudioFileClip, concatenate_audioclips
    except ImportError:
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
        except ImportError:
            print_error("moviepy not installed. Run: pip install moviepy")
            print_info("Skipping audio merge...")
            return 0
    
    try:
        # Read video path
        video_path_file = TEST_DIR / 'video_path.txt'
        if not video_path_file.exists():
            print_error("Video path file not found. Run step_07 first.")
            return 1
        video_path = video_path_file.read_text().strip()
        
        if not Path(video_path).exists():
            print_error(f"Video file not found: {video_path}")
            return 1
        
        # Read audio files list
        audio_info_file = TEST_DIR / 'audio_clips.json'
        if not audio_info_file.exists():
            print_error("Audio clips info file not found. Run step_09 first.")
            return 1
        audio_files = json.loads(audio_info_file.read_text())
        
        if not audio_files or len(audio_files) == 0:
            print_error("No audio files to merge - returning silent video")
            print_info(f"Silent video location: {video_path}")
            return 0
        
        print_info(f"Found {len(audio_files)} audio files to merge")
        
        print_info("Loading video file...")
        video = VideoFileClip(video_path)
        video_duration = video.duration
        print_info(f"Video duration: {video_duration:.2f}s")
        
        # Concatenate all audio clips
        print_info("Concatenating audio clips...")
        audio_clips = []
        total_audio_duration = 0
        
        for i, audio_file in enumerate(audio_files):
            if not Path(audio_file).exists():
                print_error(f"Audio file not found: {audio_file}")
                continue
            audio_clip = AudioFileClip(str(audio_file))
            audio_clips.append(audio_clip)
            duration = audio_clip.duration
            total_audio_duration += duration
            print_info(f"  Clip {i}: {duration:.2f}s")
        
        if not audio_clips:
            print_error("No valid audio clips to merge")
            video.close()
            return 1
        
        full_audio = concatenate_audioclips(audio_clips)
        print_info(f"Total audio duration: {total_audio_duration:.2f}s")
        
        # Check alignment
        duration_diff = abs(video_duration - total_audio_duration)
        if duration_diff > 2.0:
            print_error(f"WARNING: Duration mismatch of {duration_diff:.2f}s")
            print_info(f"Video: {video_duration:.2f}s, Audio: {total_audio_duration:.2f}s")
            
            # Pad audio if shorter
            if total_audio_duration < video_duration:
                try:
                    from moviepy import AudioClip
                except ImportError:
                    from moviepy.editor import AudioClip
                silence_duration = video_duration - total_audio_duration
                silence = AudioClip(lambda t: 0, duration=silence_duration)
                full_audio = concatenate_audioclips([full_audio, silence])
                print_info(f"Padded audio with {silence_duration:.2f}s silence")
        else:
            print_success(f"Good alignment! Difference: {duration_diff:.2f}s")
        
        # Attach audio to video
        print_info("Attaching audio to video...")
        # moviepy 2.x uses with_audio, 1.x uses set_audio
        if hasattr(video, 'with_audio'):
            final_video = video.with_audio(full_audio)
        else:
            final_video = video.set_audio(full_audio)
        
        # Save final video
        output_path = TEST_DIR / 'final_video_with_audio.mp4'
        print_info(f"Saving final video to: {output_path}")
        print_info("This may take 1-2 minutes...")
        
        final_video.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            logger=None,
            fps=60
        )
        
        # Cleanup
        video.close()
        full_audio.close()
        for clip in audio_clips:
            clip.close()
        
        print_success(f"Final video created: {output_path}")
        print_info(f"Final size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Save final video path
        final_path_file = TEST_DIR / 'final_video_path.txt'
        final_path_file.write_text(str(output_path))
        
        return 0
        
    except Exception as e:
        print_error(f"Failed to merge audio and video: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

