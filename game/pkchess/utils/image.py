from PIL import Image
import numpy as np

__all__ = ["replace_color"]


# noinspection PyUnresolvedReferences
def replace_color(image_path: str, original: (int, int, int), new: (int, int, int)) -> Image:
    im = Image.open(image_path).convert("RGBA")

    data = np.array(im)
    red, green, blue, alpha = data.T

    areas_to_replace = (red == original[0]) & (green == original[1]) & (blue == original[2])
    data[..., :-1][areas_to_replace.T] = new

    return Image.fromarray(data)
