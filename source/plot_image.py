"""Opens a background image for use in combined Dash visualisations."""

from typing import Optional

from dash import Dash, html
from PIL import Image


def pimage(infile: str) -> Optional[Image.Image]:
    """Open an image file and return it as a PIL Image.

    Args:
        infile: Path to the image file to open.

    Returns:
        The opened PIL Image object, or None if the file could not be read.

    Raises:
        FileNotFoundError: If the image file does not exist.
        IOError: If the file exists but cannot be accessed.
    """
    print(f"Image: {infile}")

    try:
        pil_image = Image.open(infile)
        return pil_image

    except FileNotFoundError:
        print("File does not exist.")

    except IOError:
        print("File exists but is not accessible.")

    return None


def _run_image_app(infile: str) -> None:
    """Display an image in a standalone Dash app (for direct execution).

    Args:
        infile: Path to the image file to display.
    """
    pil_image = pimage(infile)
    if pil_image is None:
        return

    app = Dash(__name__)
    app.layout = html.Div([
        html.Img(src=pil_image, style={'width': '100%', 'height': 'auto'}),
        html.H1(infile)
    ])
    app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    print("Executing directly")
    _run_image_app(infile="../test_data/COL_72_09_17_1705_LHZ.png")
