import ffmpeg
import subprocess  # For more reliable video concatenation
import os
import shutil  # To check if ffmpeg is installed

def check_ffmpeg_installed():
    """Check if FFmpeg is installed on the system"""
    if shutil.which("ffmpeg") is None:
        raise EnvironmentError("FFmpeg not found. Please install FFmpeg and ensure it's in your system's PATH.")

def overlay_image(
    input_video_path: str,
    image_path: str,
    output_video_path: str,
    x: str = '10',  # Default x coordinate (top-left)
    y: str = '10'   # Default y coordinate (top-left)
):
    """
    Overlay an image on a video.

    Args:
        input_video_path (str): Input video file path.
        image_path (str): Path to the image file to overlay.
        output_video_path (str): Output video file path.
        x (str): X coordinate for image overlay (FFmpeg syntax, e.g., '10', 'main_w-overlay_w-10').
        y (str): Y coordinate for image overlay (FFmpeg syntax, e.g., '10', 'main_h-overlay_h-10').
    """
    check_ffmpeg_installed()
    print(f"Overlaying image '{image_path}' onto '{input_video_path}'...")
    try:
        in_video = ffmpeg.input(input_video_path)
        in_image = ffmpeg.input(image_path)

        # Use overlay filter, ensuring original audio stream is preserved
        # [0:v] represents the video stream of the first input (video)
        # [1:v] represents the video stream of the second input (image) (image treated as single-frame video)
        # [0:a?] represents the audio stream of the first input (video) (if it exists '?')
        processed_video = ffmpeg.overlay(in_video['v'], in_image['v'], x=x, y=y)

        # Output by combining processed video stream and original audio stream
        stream = ffmpeg.output(
            processed_video,             # Processed video stream
            in_video['a?'],              # Original audio stream (if exists)
            output_video_path,
            vcodec='libx264',            # Choose suitable video codec
            acodec='aac',                # Choose suitable audio codec
            strict='experimental',       # Sometimes needed
            **{'qscale:v': '3'}          # Control video quality (optional, lower value = better quality)
        )
        # Run ffmpeg command, overwrite existing output file
        ffmpeg.run(stream, overwrite_output=True, quiet=False)  # quiet=False to show FFmpeg output
        print(f"Image overlay complete. Output: '{output_video_path}'")
    except ffmpeg.Error as e:
        print("FFmpeg Error during image overlay:")
        print(e.stderr.decode())  # Print FFmpeg's error output
        raise  # Re-raise the exception

def overlay_audio(
    input_video_path: str,
    input_audio_path: str,
    output_video_path: str,
    volume_video: float = 1.0,   # Original video volume
    volume_overlay: float = 0.7  # Overlay audio volume (e.g., background music usually quieter)
):
    """
    Overlay (mix) an audio file with a video's existing audio track.
    If the video has no audio track, simply adds the audio to the video.

    Args:
        input_video_path (str): Input video file path.
        input_audio_path (str): Path to the audio file to overlay.
        output_video_path (str): Output video file path.
        volume_video (float): Volume factor for the original video audio track (1.0 = 100%).
        volume_overlay (float): Volume factor for the overlay audio track (1.0 = 100%).
    """
    check_ffmpeg_installed()
    print(f"Overlaying audio '{input_audio_path}' onto '{input_video_path}'...")
    try:
        # First, check if the video has an audio stream
        probe = ffmpeg.probe(input_video_path)
        has_audio = any(stream["codec_type"] == "audio" for stream in probe["streams"])
        
        in_video = ffmpeg.input(input_video_path)
        in_audio = ffmpeg.input(input_audio_path)
        
        # Adjust the audio overlay volume
        overlay_audio = in_audio['a'].filter('volume', volume=volume_overlay)
        
        # Different handling depending on whether input video has audio
        if has_audio:
            print("Input video has audio stream. Mixing with overlay audio...")
            # Prepare video's audio with adjusted volume
            video_audio = in_video['a'].filter('volume', volume=volume_video)
            
            # Mix the two audio streams
            mixed_audio = ffmpeg.filter([video_audio, overlay_audio], 
                                      'amix', 
                                      inputs=2, 
                                      duration='first', 
                                      dropout_transition=1)
        else:
            print("Input video has no audio stream. Using overlay audio directly...")
            # If no audio in video, use the overlay audio directly
            mixed_audio = overlay_audio

        # Output using original video stream and processed audio stream
        stream = ffmpeg.output(
            in_video['v'],       # Video stream
            mixed_audio,         # Audio stream (either mixed or direct overlay)
            output_video_path,
            vcodec='copy',       # Copy video stream to avoid re-encoding
            acodec='aac',        # Audio codec
            strict='experimental',
            shortest=None        # Ensure output duration matches video
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=False)
        print(f"Audio overlay complete. Output: '{output_video_path}'")
    except ffmpeg.Error as e:
        print("FFmpeg Error during audio overlay:")
        # Try to print FFmpeg's stderr output
        stderr_output = getattr(e, 'stderr', None)
        if stderr_output:
            print(stderr_output.decode())
        else:
            print(f"An unexpected ffmpeg error occurred: {e}")
        raise

def concatenate_videos(video_paths: list, output_video_path: str):
    """
    Use FFmpeg concat demuxer to concatenate multiple video files.
    Note: This method requires all input videos to have the same codec, resolution, framerate, etc.
    If parameters differ, transcoding or using a more complex filter (like concat filter) is needed.

    Args:
        video_paths (list): List of video file paths to concatenate (in order).
        output_video_path (str): Output path for the concatenated video.
    """
    check_ffmpeg_installed()
    if not video_paths or len(video_paths) < 2:
        print("Need at least two videos to concatenate.")
        return

    print(f"Concatenating videos: {video_paths}...")

    # 1. Create temporary file list mylist.txt
    list_file_path = "mylist.txt"  # Place in project root, delete at end
    try:
        with open(list_file_path, 'w', encoding='utf-8') as f:
            for path in video_paths:
                # Handle Windows path backslashes and special characters, ensuring FFmpeg parses correctly
                # Use repr() to add quotes and escape special characters, then remove outer single quotes
                safe_path = repr(os.path.abspath(path))[1:-1]
                f.write(f"file '{safe_path}'\n")
        print(f"Generated temporary list file: {list_file_path}")

        # 2. Build FFmpeg command
        # -f concat: Use concat demuxer
        # -safe 0: Allow absolute paths or paths with special characters (works with safe_path above)
        # -i mylist.txt: Specify input file list
        # -c copy: Direct stream copy, no re-encoding (fast, but requires consistent format)
        command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file_path,
            '-c', 'copy',  # If video formats not completely identical, may need to remove '-c copy' for re-encoding
            output_video_path
        ]

        print(f"Executing FFmpeg command: {' '.join(command)}")

        # 3. Execute FFmpeg command
        process = subprocess.run(command, capture_output=True, text=True, check=False)  # check=False for manual checking

        # 4. Check results
        if process.returncode != 0:
            print("FFmpeg Error during concatenation:")
            print("STDOUT:", process.stdout)
            print("STDERR:", process.stderr)
            raise RuntimeError(f"FFmpeg concatenation failed with return code {process.returncode}")
        else:
            print(f"Video concatenation complete. Output: '{output_video_path}'")
            # print("FFmpeg Output:", process.stdout)  # Optional: Print output on success

    except Exception as e:
        print(f"An error occurred during concatenation: {e}")
        raise
    finally:
        # 5. Delete temporary file
        if os.path.exists(list_file_path):
            os.remove(list_file_path)
            print(f"Removed temporary list file: {list_file_path}")