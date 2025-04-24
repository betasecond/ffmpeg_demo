# FFmpeg Video Processing Project

This project automates a series of video processing tasks using FFmpeg and Python. It handles QR code generation, video overlays, audio mixing, and video concatenation to create a final composite video.

## Features

- **QR Code Generation**: Creates a QR code with an embedded logo for a specified URL
- **Video Processing**:
  - Overlay QR code image onto a video
  - Mix audio tracks with existing video
  - Concatenate multiple videos into a single file
- **Modular Design**: Core functionality organized into reusable Python modules

## Prerequisites

- Python 3.6 or higher
- FFmpeg installed and available in your system PATH
- Python packages listed in `requirements.txt`

## Directory Structure

```
ffmpeg_demo/
├── input/                     # Input files directory
│   ├── ch1.mp4                # First input video
│   ├── ch2.mp4                # Second input video
│   ├── target.m4a             # Audio file to overlay
│   └── img.jpg                # Logo for QR code
├── output/                    # Output files directory (created automatically)
│   ├── qr_code_with_logo.png  # Generated QR code with logo
│   ├── intermediate_1_qr.mp4  # Video with QR code overlay
│   ├── intermediate_2_audio.mp4 # Video with audio overlay
│   └── final_output.mp4       # Final concatenated video
├── lib/                       # Library modules
│   ├── __init__.py
│   ├── ffmpeg_utils.py        # FFmpeg-related functions
│   └── qr_code_utils.py       # QR code generation functions
├── main.py                    # Main script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

1. Clone this repository:
   ```
   git clone [repository-url]
   cd ffmpeg_demo
   ```

2. Ensure FFmpeg is installed on your system:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `apt install ffmpeg` or equivalent for your distribution

3. Install Python dependencies using uv with Tsinghua Mirror:
   ```
   uv pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

   Or using regular pip:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your input files in the `input/` directory:
   - `ch1.mp4`: First video to process
   - `ch2.mp4`: Second video to concatenate
   - `target.m4a`: Audio file to overlay
   - `img.jpg`: Logo image to embed in QR code

2. Run the main script:
   ```
   python main.py
   ```

3. Check the `output/` directory for the processed files:
   - `qr_code_with_logo.png`: Generated QR code with logo
   - `intermediate_1_qr.mp4`: First video with QR code overlay
   - `intermediate_2_audio.mp4`: First video with QR code and audio overlay
   - `final_output.mp4`: Final concatenated video

## Customizing the Process

Edit `main.py` to modify:

- `URL_TO_ENCODE`: The URL to encode in the QR code
- `OVERLAY_X` and `OVERLAY_Y`: Position of QR code overlay on the video
- Input and output file paths
- Audio mixing volumes

## Module Documentation

### QR Code Utilities (`qr_code_utils.py`)

- `generate_qr_code_with_logo(url, output_path, logo_path, scale, border)`
  - Generates a QR code for the specified URL and embeds a logo in the center
  - Parameters:
    - `url`: URL to encode
    - `output_path`: Path to save the generated QR code
    - `logo_path`: Path to the logo image
    - `scale`: Size of QR code modules (pixels)
    - `border`: Width of QR code border (modules)

### FFmpeg Utilities (`ffmpeg_utils.py`)

- `overlay_image(input_video_path, image_path, output_video_path, x, y)`
  - Overlays an image onto a video
  - Parameters:
    - `input_video_path`: Path to the input video
    - `image_path`: Path to the image to overlay
    - `output_video_path`: Path to save the output video
    - `x`, `y`: Coordinates for image placement

- `overlay_audio(input_video_path, input_audio_path, output_video_path, volume_video, volume_overlay)`
  - Mixes an audio file with a video's audio track
  - Parameters:
    - `input_video_path`: Path to the input video
    - `input_audio_path`: Path to the audio file
    - `output_video_path`: Path to save the output video
    - `volume_video`: Volume factor for original video audio
    - `volume_overlay`: Volume factor for overlay audio

- `concatenate_videos(video_paths, output_video_path)`
  - Joins multiple videos into a single file
  - Parameters:
    - `video_paths`: List of video file paths to concatenate
    - `output_video_path`: Path to save the concatenated video

## Troubleshooting

- **FFmpeg Not Found**: Ensure FFmpeg is installed and in your system PATH
- **Audio Overlay Issues**: Make sure input videos contain audio tracks or use the updated function that handles videos without audio
- **Concatenation Problems**: For best results, input videos should have the same codec, resolution, and framerate

## License

[Specify your license here]

## Acknowledgments

- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
- [PyQRCode](https://github.com/mnooner256/pyqrcode)
- [Pillow](https://python-pillow.org/)