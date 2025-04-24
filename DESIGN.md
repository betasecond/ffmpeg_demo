## **项目设计文档：FFmpeg 视频处理流程**

### 1. 项目目标

本项目旨在创建一个 Python 应用程序，利用 FFmpeg 和相关库，自动化执行一系列视频编辑任务。具体流程包括：

1.  **二维码生成与嵌入**：为指定 URL (例如 `google.com`) 生成二维码，并将一个 logo 图片 (`input/img.jpg`) 嵌入二维码中心。
2.  **图片叠加**：将生成的带 logo 的二维码图片叠加到视频 `input/ch1.mp4` 的指定位置。
3.  **声轨叠加**：将 `input/target.m4a` 的音频与上一步处理后的视频进行混合（叠加）。
4.  **视频拼接**：将上一步处理后的视频与 `input/ch2.mp4` 进行拼接，生成最终的输出视频。

项目要求采用模块化设计，将核心功能封装在可重用的库函数中，并通过 `main.py` 脚本调用这些函数来完成特定任务。

### 2. 项目结构

根据你的现有目录和需求，建议采用以下结构：

```
ffmpeg_demo/
├── .venv/                     # Python 虚拟环境 (已存在)
├── .idea/                     # PyCharm 项目配置 (已存在)
├── input/                     # 输入文件目录 (已存在)
│   ├── ch1.mp4
│   ├── ch2.mp4
│   ├── target.m4a
│   └── img.jpg                # <--- 需要添加的 Logo 图片
├── output/                    # 输出文件目录 (需要创建)
│   ├── qr_code_with_logo.png  # 生成的带 Logo 二维码
│   ├── intermediate_1.mp4     # ch1 + 二维码
│   ├── intermediate_2.mp4     # ch1 + 二维码 + target.m4a 音频
│   └── final_output.mp4       # 最终拼接视频
├── lib/                       # 可重用库函数 (Agents)
│   ├── __init__.py            # 使 lib 成为一个 Python 包
│   ├── ffmpeg_utils.py        # FFmpeg 相关操作函数
│   └── qr_code_utils.py       # 二维码生成相关函数
├── main.py                    # 主执行脚本
├── pyproject.toml             # 项目元数据 (已存在)
├── requirements.txt           # 项目依赖列表 (需要创建)
└── .gitignore                 # Git 忽略配置 (已存在, 可更新)
```

**说明:**

*   **`input/img.jpg`**: 你需要准备一个 logo 图片放在 `input` 目录下，用于嵌入二维码。
*   **`output/`**: 用于存放所有生成的文件，包括中间文件和最终结果。建议将其添加到 `.gitignore`。
*   **`lib/`**: 存放核心处理逻辑。
*   **`requirements.txt`**: 列出项目所需的 Python 库。

### 3. 依赖项

本项目需要以下 Python 库：

*   **`ffmpeg-python`**: 一个 Python 封装库，用于更方便地调用 FFmpeg 命令。
*   **`pyqrcode`**: 用于生成二维码。
*   **`pypng`**: `pyqrcode` 保存 PNG 文件时需要。
*   **`Pillow`**: 用于图像处理，特别是将 logo 嵌入二维码。

**`requirements.txt` 文件内容:**

```txt
ffmpeg-python
pyqrcode
pypng
Pillow
```

**安装依赖:**

在激活虚拟环境 (`.venv`) 的情况下，运行：

```bash
pip install -r requirements.txt
```

**系统依赖:**

*   **FFmpeg**: 必须在系统环境变量 `PATH` 中能够找到 `ffmpeg` 可执行文件。`ffmpeg-python` 库本身不包含 FFmpeg，它只是一个调用接口。请确保已正确安装 FFmpeg。

### 4. 库设计 (`lib/`)

#### 4.1. 二维码生成 Agent (`lib/qr_code_utils.py`)

**目标**: 根据 URL 生成二维码，并将 logo 嵌入中心。

```python
# lib/qr_code_utils.py
import pyqrcode
import png # 需要 pypng 库
from PIL import Image
import os

def generate_qr_code_with_logo(url: str, output_path: str, logo_path: str = None, scale: int = 8, border: int = 4):
    """
    生成带有中心 Logo 的二维码图片。

    Args:
        url (str): 要编码的 URL。
        output_path (str): 输出 PNG 图片的完整路径。
        logo_path (str, optional): Logo 图片的路径。如果为 None，则生成不带 Logo 的二维码。
        scale (int, optional): 二维码模块的大小（像素）。默认为 8。
        border (int, optional): 二维码边框宽度（模块数）。默认为 4。

    Raises:
        FileNotFoundError: 如果 logo_path 指定的文件不存在。
        ValueError: 如果 logo 太大无法嵌入。
    """
    print(f"Generating QR code for URL: {url}")
    qr_code = pyqrcode.create(url, error='H') # 使用高容错率 'H'

    # 先将二维码保存为临时文件或内存对象，以便 Pillow 处理
    temp_qr_path = output_path + ".tmp.png"
    qr_code.png(temp_qr_path, scale=scale, module_color=[0, 0, 0, 255], background=[255, 255, 255, 255], quiet_zone=border)

    qr_img = Image.open(temp_qr_path).convert("RGBA")

    if logo_path:
        if not os.path.exists(logo_path):
            os.remove(temp_qr_path) # 清理临时文件
            raise FileNotFoundError(f"Logo file not found: {logo_path}")

        print(f"Embedding logo: {logo_path}")
        logo = Image.open(logo_path).convert("RGBA")

        # --- Logo 尺寸调整 ---
        # Logo 的大小不应超过二维码总面积的约 20%，以保证可读性
        # 这里简单地将 Logo 缩放到二维码宽度的 1/5 左右
        qr_width, qr_height = qr_img.size
        max_logo_size = int(min(qr_width, qr_height) * 0.20) # 限制 logo 最大尺寸

        logo.thumbnail((max_logo_size, max_logo_size)) # 等比缩放

        logo_width, logo_height = logo.size
        if logo_width == 0 or logo_height == 0:
             os.remove(temp_qr_path)
             raise ValueError("Logo size is invalid after resizing.")


        # --- 计算 Logo 粘贴位置 (居中) ---
        box_x = (qr_width - logo_width) // 2
        box_y = (qr_height - logo_height) // 2
        box = (box_x, box_y, box_x + logo_width, box_y + logo_height)

        # --- 创建白色背景层，防止 Logo 透明部分透出二维码 ---
        # 注意：更高级的方法是只在 Logo 区域清除二维码像素，但这里用白色背景简化
        background = Image.new('RGBA', (logo_width, logo_height), (255, 255, 255, 255))
        qr_img.paste(background, (box_x, box_y))

        # --- 粘贴 Logo ---
        # 使用 Logo 的 alpha 通道作为 mask 进行粘贴
        qr_img.paste(logo, box, mask=logo)
        print(f"Logo embedded at position: {box}")

    # 保存最终图片
    qr_img.save(output_path)
    print(f"QR code with logo saved to: {output_path}")

    # 清理临时文件
    os.remove(temp_qr_path)

```

#### 4.2. FFmpeg 操作 Agent (`lib/ffmpeg_utils.py`)

**目标**: 封装 FFmpeg 的核心操作：图片叠加、音频叠加、视频拼接。

```python
# lib/ffmpeg_utils.py
import ffmpeg
import subprocess # 用于更可靠的视频拼接
import os
import shutil # 用于检查 ffmpeg 是否存在

def check_ffmpeg_installed():
    """检查系统中是否安装了 FFmpeg"""
    if shutil.which("ffmpeg") is None:
        raise EnvironmentError("FFmpeg not found. Please install FFmpeg and ensure it's in your system's PATH.")

def overlay_image(
    input_video_path: str,
    image_path: str,
    output_video_path: str,
    x: str = '10', # 默认左上角 x 坐标
    y: str = '10'  # 默认左上角 y 坐标
):
    """
    在视频上叠加图片。

    Args:
        input_video_path (str): 输入视频文件路径。
        image_path (str): 要叠加的图片文件路径。
        output_video_path (str): 输出视频文件路径。
        x (str): 图片叠加的 x 坐标 (FFmpeg 语法, e.g., '10', 'main_w-overlay_w-10')。
        y (str): 图片叠加的 y 坐标 (FFmpeg 语法, e.g., '10', 'main_h-overlay_h-10')。
    """
    check_ffmpeg_installed()
    print(f"Overlaying image '{image_path}' onto '{input_video_path}'...")
    try:
        in_video = ffmpeg.input(input_video_path)
        in_image = ffmpeg.input(image_path)

        # 使用 overlay 滤镜，并确保保留原始音频流
        # [0:v] 代表第一个输入（视频）的视频流
        # [1:v] 代表第二个输入（图片）的视频流 (图片被当作单帧视频)
        # [0:a?] 代表第一个输入（视频）的音频流（如果存在 '?'）
        processed_video = ffmpeg.overlay(in_video['v'], in_image['v'], x=x, y=y)

        # 输出时合并处理后的视频流和原始音频流
        stream = ffmpeg.output(
            processed_video,             # 处理后的视频流
            in_video['a?'],              # 原始音频流 (如果存在)
            output_video_path,
            vcodec='libx264',            # 选择合适的视频编码器
            acodec='aac',                # 选择合适的音频编码器
            strict='experimental',       # 有时需要
            **{'qscale:v': '3'}          # 控制视频质量 (可选, 值越小质量越好)
        )
        # 运行 ffmpeg 命令, 覆盖已存在输出文件
        ffmpeg.run(stream, overwrite_output=True, quiet=False) # quiet=False 显示 FFMpeg 输出
        print(f"Image overlay complete. Output: '{output_video_path}'")
    except ffmpeg.Error as e:
        print("FFmpeg Error during image overlay:")
        print(e.stderr.decode()) # 打印 FFMpeg 的错误输出
        raise # 重新抛出异常

def overlay_audio(
    input_video_path: str,
    input_audio_path: str,
    output_video_path: str,
    volume_video: float = 1.0, # 原视频音量
    volume_overlay: float = 0.7 # 叠加音频音量 (例如背景音乐通常小声点)
):
    """
    将一个音频文件叠加（混合）到视频的现有音轨上。

    Args:
        input_video_path (str): 输入视频文件路径 (应包含音轨)。
        input_audio_path (str): 要叠加的音频文件路径。
        output_video_path (str): 输出视频文件路径。
        volume_video (float): 原视频音轨的音量因子 (1.0 = 100%)。
        volume_overlay (float): 叠加音轨的音量因子 (1.0 = 100%)。
    """
    check_ffmpeg_installed()
    print(f"Overlaying audio '{input_audio_path}' onto '{input_video_path}'...")
    try:
        in_video = ffmpeg.input(input_video_path)
        in_audio = ffmpeg.input(input_audio_path)

        # [0:a] 视频的音频流
        # [1:a] 叠加的音频流
        # volume=... 调整各自音量
        # amix=inputs=2:duration=first:dropout_transition=3 混合两个音频流
        # duration=first: 混合时长以第一个输入（视频音轨）为准
        # dropout_transition: 当一个流结束时，另一个流音量渐变的秒数
        mixed_audio = ffmpeg.filter(
            [in_video['a'].filter('volume', volume=volume_video),
             in_audio['a'].filter('volume', volume=volume_overlay)],
            'amix', inputs=2, duration='first', dropout_transition=1
        ).node

        # 输出时使用原始视频流和混合后的音频流
        # 使用 vcodec='copy' 避免重新编码视频，加快速度
        stream = ffmpeg.output(
            in_video['v'],             # 原始视频流
            mixed_audio,               # 混合后的音频流
            output_video_path,
            vcodec='copy',             # 复制视频流，不重新编码
            acodec='aac',              # 音频需要重新编码
            strict='experimental',
            shortest=None              # 确保输出时长由音频/视频共同决定，amix已处理时长
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=False)
        print(f"Audio overlay complete. Output: '{output_video_path}'")
    except ffmpeg.Error as e:
        print("FFmpeg Error during audio overlay:")
        # 尝试打印 FFmpeg 的 stderr 输出
        stderr_output = getattr(e, 'stderr', None)
        if stderr_output:
            print(stderr_output.decode())
        else:
            print(f"An unexpected ffmpeg error occurred: {e}")
        raise

def concatenate_videos(video_paths: list, output_video_path: str):
    """
    使用 FFmpeg concat demuxer 拼接多个视频文件。
    注意：这种方法要求所有输入视频具有相同的编解码器、分辨率、帧率等参数。
    如果参数不同，需要先进行转码或使用更复杂的 filter (如 concat filter)。

    Args:
        video_paths (list): 包含要拼接的视频文件路径的列表 (按顺序)。
        output_video_path (str): 输出的拼接视频文件路径。
    """
    check_ffmpeg_installed()
    if not video_paths or len(video_paths) < 2:
        print("Need at least two videos to concatenate.")
        return

    print(f"Concatenating videos: {video_paths}...")

    # 1. 创建临时的文件列表 list.txt
    list_file_path = "mylist.txt" # 放在项目根目录，最后删除
    try:
        with open(list_file_path, 'w', encoding='utf-8') as f:
            for path in video_paths:
                # 处理 Windows 路径的反斜杠和特殊字符，确保 FFmpeg 能正确解析
                # 使用 repr() 添加引号并转义特殊字符，然后去除外层单引号
                safe_path = repr(os.path.abspath(path))[1:-1]
                f.write(f"file '{safe_path}'\n")
        print(f"Generated temporary list file: {list_file_path}")

        # 2. 构建 FFmpeg 命令
        # -f concat: 使用 concat demuxer
        # -safe 0: 允许使用绝对路径或包含特殊字符的路径 (配合上面的 safe_path 处理)
        # -i mylist.txt: 指定输入文件列表
        # -c copy: 直接复制流，不重新编码 (快速，但要求格式一致)
        command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file_path,
            '-c', 'copy', # 如果视频格式不完全一致，可能需要去掉 '-c copy' 进行重新编码
            output_video_path
        ]

        print(f"Executing FFmpeg command: {' '.join(command)}")

        # 3. 执行 FFmpeg 命令
        process = subprocess.run(command, capture_output=True, text=True, check=False) # check=False 手动检查

        # 4. 检查结果
        if process.returncode != 0:
            print("FFmpeg Error during concatenation:")
            print("STDOUT:", process.stdout)
            print("STDERR:", process.stderr)
            raise RuntimeError(f"FFmpeg concatenation failed with return code {process.returncode}")
        else:
            print(f"Video concatenation complete. Output: '{output_video_path}'")
            # print("FFmpeg Output:", process.stdout) # 可选：打印成功时的输出

    except Exception as e:
        print(f"An error occurred during concatenation: {e}")
        raise
    finally:
        # 5. 删除临时文件
        if os.path.exists(list_file_path):
            os.remove(list_file_path)
            print(f"Removed temporary list file: {list_file_path}")

```

### 5. 主脚本设计 (`main.py`)

**目标**: 调用 `lib` 中的函数，按顺序执行用户指定的视频处理流程。

```python
# main.py
import os
import sys
from lib import ffmpeg_utils
from lib import qr_code_utils

# --- 配置参数 ---
INPUT_DIR = "input"
OUTPUT_DIR = "output"
URL_TO_ENCODE = "https://google.com"
LOGO_FILENAME = "img.jpg" # Logo 文件名，放在 INPUT_DIR 下

# 输入文件名
VIDEO1_FILENAME = "ch1.mp4"
VIDEO2_FILENAME = "ch2.mp4"
AUDIO_OVERLAY_FILENAME = "target.m4a"

# 输出和中间文件名
QR_CODE_FILENAME = "qr_code_with_logo.png"
INTERMEDIATE_VIDEO1 = "intermediate_1_qr.mp4"
INTERMEDIATE_VIDEO2 = "intermediate_2_audio.mp4"
FINAL_OUTPUT_FILENAME = "final_output.mp4"

# 图片叠加位置 (FFmpeg 语法)
OVERLAY_X = 'main_w-overlay_w-10' # 右边距 10px
OVERLAY_Y = '10'                  # 上边距 10px

# --- 主函数 ---
def main():
    # 1. 检查 FFmpeg 是否安装
    try:
        ffmpeg_utils.check_ffmpeg_installed()
    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1) # 退出程序

    # 2. 确保输入文件存在
    video1_path = os.path.join(INPUT_DIR, VIDEO1_FILENAME)
    video2_path = os.path.join(INPUT_DIR, VIDEO2_FILENAME)
    audio_path = os.path.join(INPUT_DIR, AUDIO_OVERLAY_FILENAME)
    logo_path = os.path.join(INPUT_DIR, LOGO_FILENAME)

    required_files = [video1_path, video2_path, audio_path, logo_path]
    for f_path in required_files:
        if not os.path.exists(f_path):
            print(f"Error: Input file not found at '{f_path}'")
            sys.exit(1)

    # 3. 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: '{os.path.abspath(OUTPUT_DIR)}'")

    # 4. 定义输出文件路径
    qr_output_path = os.path.join(OUTPUT_DIR, QR_CODE_FILENAME)
    intermediate1_output_path = os.path.join(OUTPUT_DIR, INTERMEDIATE_VIDEO1)
    intermediate2_output_path = os.path.join(OUTPUT_DIR, INTERMEDIATE_VIDEO2)
    final_output_path = os.path.join(OUTPUT_DIR, FINAL_OUTPUT_FILENAME)

    try:
        # --- 步骤 1: 生成带 Logo 的二维码 ---
        print("\n--- Step 1: Generating QR Code ---")
        qr_code_utils.generate_qr_code_with_logo(
            url=URL_TO_ENCODE,
            output_path=qr_output_path,
            logo_path=logo_path,
            scale=10 # 调大 scale 使二维码更清晰，Logo 更易嵌入
        )

        # --- 步骤 2: 将二维码叠加到 ch1.mp4 ---
        print("\n--- Step 2: Overlaying QR Code onto Video 1 ---")
        ffmpeg_utils.overlay_image(
            input_video_path=video1_path,
            image_path=qr_output_path,
            output_video_path=intermediate1_output_path,
            x=OVERLAY_X,
            y=OVERLAY_Y
        )

        # --- 步骤 3: 将 target.m4a 音频叠加到上一步结果 ---
        print("\n--- Step 3: Overlaying Audio onto Intermediate Video 1 ---")
        ffmpeg_utils.overlay_audio(
            input_video_path=intermediate1_output_path,
            input_audio_path=audio_path,
            output_video_path=intermediate2_output_path,
            volume_video=1.0,   # 保持原视频音量
            volume_overlay=0.8  # 叠加音频的音量稍小
        )

        # --- 步骤 4: 拼接处理后的视频和 ch2.mp4 ---
        print("\n--- Step 4: Concatenating Videos ---")
        videos_to_concat = [
            os.path.abspath(intermediate2_output_path), # 使用绝对路径更可靠
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
    except (ffmpeg.Error, RuntimeError, Exception) as e:
        print(f"\nAn error occurred during processing: {e}")
        # 可以在这里添加更详细的错误记录或清理逻辑
        sys.exit(1)
    finally:
        # 可选：清理中间文件 (如果不需要保留)
        # print("\nCleaning up intermediate files...")
        # files_to_remove = [qr_output_path, intermediate1_output_path, intermediate2_output_path]
        # for f in files_to_remove:
        #     if os.path.exists(f):
        #         try:
        #             os.remove(f)
        #             print(f"Removed: {f}")
        #         except OSError as e:
        #             print(f"Error removing {f}: {e}")
        pass # 暂时不清理，方便调试

if __name__ == "__main__":
    main()
```

### 6. 设置与执行

1.  **准备环境**:
    *   确保已安装 Python 3.x。
    *   确保已安装 FFmpeg 并将其添加到系统 PATH。
    *   创建项目目录结构如第 2 节所示。
    *   将你的视频 `ch1.mp4`, `ch2.mp4`, 音频 `target.m4a` 和 Logo 图片 `img.jpg` 放入 `input/` 目录。
    *   创建 `requirements.txt` 文件并填入第 3 节的内容。
    *   将第 4 节的代码分别保存到 `lib/qr_code_utils.py` 和 `lib/ffmpeg_utils.py`。创建空的 `lib/__init__.py` 文件。
    *   将第 5 节的代码保存到 `main.py`。
2.  **安装依赖**:
    *   打开命令行/终端，导航到 `ffmpeg_demo` 目录。
    *   激活你的虚拟环境（如果你正在使用，例如 `.venv\Scripts\activate` on Windows）。
    *   运行 `pip install -r requirements.txt`。
3.  **执行脚本**:
    *   在激活虚拟环境的终端中，运行 `python main.py`。
4.  **查看结果**:
    *   脚本执行过程中会打印各个步骤的信息和 FFmpeg 的输出。
    *   执行成功后，检查 `output/` 目录，应包含生成的二维码图片、中间视频和最终的 `final_output.mp4`。

### 7. 未来考虑与改进

*   **错误处理**: 增强错误处理，例如检查 FFmpeg 命令的返回值和 `stderr` 输出，提供更具体的错误信息。
*   **配置化**: 将输入/输出文件名、URL、叠加位置等参数移到配置文件（如 JSON 或 YAML）或命令行参数中，使脚本更灵活。
*   **视频参数一致性**: `concatenate_videos` 使用的 `concat` demuxer 对输入视频格式要求严格。如果输入视频参数（分辨率、编码器、帧率等）不一致，需要改用 `concat` filter，这会更复杂但更通用，涉及重新编码。`ffmpeg_utils.py` 中可以增加一个使用 filter 的拼接函数。
*   **性能**: 对于大型文件，考虑优化 FFmpeg 参数（例如，使用硬件加速（如 `-hwaccel cuda`），调整编码预设）。
*   **进度条**: 对于长时间运行的任务，可以考虑使用 `tqdm` 等库来显示进度。
*   **日志记录**: 使用 Python 的 `logging` 模块记录详细的操作日志，方便调试和追踪。
*   **Logo 嵌入健壮性**: `generate_qr_code_with_logo` 中 Logo 的大小和位置计算可以更精细，确保在各种二维码尺寸下都能良好工作且不严重影响识别率。

---

这份设计文档提供了项目的蓝图。按照这个结构和代码实现，你应该能够搭建起满足你需求的视频处理流程。记得根据你的具体环境和文件调整代码中的路径和参数。