from PIL import Image, UnidentifiedImageError
import io



def is_valid_webp(file_storage) -> bool:
    file_bytes = file_storage.read()
    file_storage.stream.seek(0)
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify() # Check file integrity
            return img.format == 'WEBP'
    except (UnidentifiedImageError, OSError):
        return False
