import base64
from io import BytesIO
from PIL import Image
import traceback


def crop_image(img_path, coords, img_type, output_file="temp_img.jpg"):
    try:
        image = Image.open(img_path)
        cropped_image = image.crop(coords)

        if img_type == "path":
            cropped_image.save(output_file, format="JPEG")
            return output_file
        elif img_type == "base64":
            buffered = BytesIO()
            cropped_image.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue())
        else:
            return False
    except Exception as e:
        traceback.print_exc()
        return False
