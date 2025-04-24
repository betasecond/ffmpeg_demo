import os
import sys
from lib import ffmpeg_utils
from lib import qr_code_utils

# --- Configuration Parameters ---
INPUT_DIR = "input"
OUTPUT_DIR = "output"
URL_TO_ENCODE = "https://google.com"
LOGO_FILENAME = "img.jpg"  # Logo filename, placed in INPUT_DIR

# Input filenames
VIDEO1_FILENAME = "ch1.mp4"
VIDEO2_FILENAME = "ch2.mp4"
AUDIO_OVERLAY_FILENAME = "target.m4a"

# Output and intermediate filenames
QR_CODE_FILENAME = "qr_code_with_logo.png"
INTERMEDIATE_VIDEO1 = "intermediate_1_qr.mp4"
INTERMEDIATE_VIDEO2 = "intermediate_2_audio.mp4"
FINAL_OUTPUT_FILENAME = "final_output.mp4"

# Image overlay position (FFmpeg syntax)
OVERLAY_X = 'main_w-overlay_w-10'  # 10px from right edge
OVERLAY_Y = '10'                   # 10px from top edge

# --- Main function ---
def main():
    # 1. Check if FFmpeg is installed
    try:
        ffmpeg_utils.check_ffmpeg_installed()
    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit program

    # 2. Ensure input files exist
    video1_path = os.path.join(INPUT_DIR, VIDEO1_FILENAME)
    video2_path = os.path.join(INPUT_DIR, VIDEO2_FILENAME)
    audio_path = os.path.join(INPUT_DIR, AUDIO_OVERLAY_FILENAME)
    logo_path = os.path.join(INPUT_DIR, LOGO_FILENAME)

    required_files = [video1_path, video2_path, audio_path, logo_path]
    for f_path in required_files:
        if not os.path.exists(f_path):
            print(f"Error: Input file not found at '{f_path}'")
            sys.exit(1)

    # 3. Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: '{os.path.abspath(OUTPUT_DIR)}'")

    # 4. Define output file paths
    qr_output_path = os.path.join(OUTPUT_DIR, QR_CODE_FILENAME)
    intermediate1_output_path = os.path.join(OUTPUT_DIR, INTERMEDIATE_VIDEO1)
    intermediate2_output_path = os.path.join(OUTPUT_DIR, INTERMEDIATE_VIDEO2)
    final_output_path = os.path.join(OUTPUT_DIR, FINAL_OUTPUT_FILENAME)

    try:
        # --- Step 1: Generate QR code with Logo ---
        print("\n--- Step 1: Generating QR Code ---")
        qr_code_utils.generate_qr_code_with_logo(
            url=URL_TO_ENCODE,
            output_path=qr_output_path,
            logo_path=logo_path,
            scale=10  # Increase scale for clearer QR code, easier logo embedding
        )

        # --- Step 2: Overlay QR code onto ch1.mp4 ---
        print("\n--- Step 2: Overlaying QR Code onto Video 1 ---")
        ffmpeg_utils.overlay_image(
            input_video_path=video1_path,
            image_path=qr_output_path,
            output_video_path=intermediate1_output_path,
            x=OVERLAY_X,
            y=OVERLAY_Y
        )

        # --- Step 3: Overlay target.m4a audio onto previous result ---
        print("\n--- Step 3: Overlaying Audio onto Intermediate Video 1 ---")
        ffmpeg_utils.overlay_audio(
            input_video_path=intermediate1_output_path,
            input_audio_path=audio_path,
            output_video_path=intermediate2_output_path,
            volume_video=1.0,    # Keep original video volume
            volume_overlay=0.8   # Slightly lower overlay audio volume
        )

        # --- Step 4: Concatenate processed video and ch2.mp4 ---
        print("\n--- Step 4: Concatenating Videos ---")
        videos_to_concat = [
            os.path.abspath(intermediate2_output_path),  # Use absolute paths for reliability
            os.path.abspath(video2_path)
        ]
        ffmpeg_utils.concatenate_videos(
            video_paths=videos_to_concat,
            output_video_path=final_output_path
        )

        print("\n--- Processing Complete! ---")
        print(f"Final video saved to: '{final_output_path}'")

    except FileNotFoundError as e:
        print(f"\nError: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")
        sys.exit(1)
    finally:
        # Optional: Clean up intermediate files (if not needed)
        # print("\nCleaning up intermediate files...")
        # files_to_remove = [qr_output_path, intermediate1_output_path, intermediate2_output_path]
        # for f in files_to_remove:
        #     if os.path.exists(f):
        #         try:
        #             os.remove(f)
        #             print(f"Removed: {f}")
        #         except OSError as e:
        #             print(f"Error removing {f}: {e}")
        pass  # Don't clean up for now, helps with debugging

if __name__ == "__main__":
    main()