import pyqrcode
import png  # needs pypng library
from PIL import Image
import os

def generate_qr_code_with_logo(url: str, output_path: str, logo_path: str = None, scale: int = 8, border: int = 4):
    """
    Generate a QR code with a centered logo.

    Args:
        url (str): URL to encode in the QR code.
        output_path (str): Complete path for the output PNG image.
        logo_path (str, optional): Path to the logo image. If None, generates QR code without a logo.
        scale (int, optional): Size of QR code modules (pixels). Default is 8.
        border (int, optional): Width of QR code border (modules). Default is 4.

    Raises:
        FileNotFoundError: If the specified logo file doesn't exist.
        ValueError: If the logo is too large to embed.
    """
    print(f"Generating QR code for URL: {url}")
    qr_code = pyqrcode.create(url, error='H')  # Use high error correction level 'H'

    # Save QR code as temporary file for Pillow processing
    temp_qr_path = output_path + ".tmp.png"
    qr_code.png(temp_qr_path, scale=scale, module_color=[0, 0, 0, 255], background=[255, 255, 255, 255], quiet_zone=border)

    qr_img = Image.open(temp_qr_path).convert("RGBA")

    if logo_path:
        if not os.path.exists(logo_path):
            os.remove(temp_qr_path)  # Clean up temporary file
            raise FileNotFoundError(f"Logo file not found: {logo_path}")

        print(f"Embedding logo: {logo_path}")
        logo = Image.open(logo_path).convert("RGBA")

        # --- Logo size adjustment ---
        # Logo size should not exceed about 20% of the QR code total area for readability
        # Simply scale the logo to about 1/5 of the QR code width
        qr_width, qr_height = qr_img.size
        max_logo_size = int(min(qr_width, qr_height) * 0.20)  # Limit max logo size

        logo.thumbnail((max_logo_size, max_logo_size))  # Proportional scaling

        logo_width, logo_height = logo.size
        if logo_width == 0 or logo_height == 0:
             os.remove(temp_qr_path)
             raise ValueError("Logo size is invalid after resizing.")

        # --- Calculate logo paste position (centered) ---
        box_x = (qr_width - logo_width) // 2
        box_y = (qr_height - logo_height) // 2
        box = (box_x, box_y, box_x + logo_width, box_y + logo_height)

        # --- Create white background layer to prevent logo's transparent parts from showing QR code ---
        # Note: A more advanced method would be to only clear QR code pixels in the logo area, but we're simplifying with a white background
        background = Image.new('RGBA', (logo_width, logo_height), (255, 255, 255, 255))
        qr_img.paste(background, (box_x, box_y))

        # --- Paste logo ---
        # Use logo's alpha channel as a mask for pasting
        qr_img.paste(logo, box, mask=logo)
        print(f"Logo embedded at position: {box}")

    # Save final image
    qr_img.save(output_path)
    print(f"QR code with logo saved to: {output_path}")

    # Clean up temporary file
    os.remove(temp_qr_path)