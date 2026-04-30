from flask import jsonify
from functools import wraps
from pymongo.errors import ServerSelectionTimeoutError
from mongoengine.errors import OperationError, NotUniqueError
import io, os, tempfile
from ffmpy import FFmpeg
from werkzeug.datastructures import FileStorage


def handle_db_timeout(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ServerSelectionTimeoutError as e:
            return jsonify({'error': 'Cannot connect to database'}), 500
        except NotUniqueError as e:
            return jsonify({'error': 'Duplicate entry'}), 409
        except OperationError as e:
            return jsonify({'error': 'Database operation failed'}), 500

    return wrapper


def serialize(doc):
    data = doc.to_mongo().to_dict()
    if '_id' in data:
        data['_id'] = str(data['_id'])
    return data


class AudioConverter:
    @staticmethod
    def to_mp3(file: FileStorage, extension: str, bitrate: str = "192k") -> FileStorage:
        """Convert audio file to mp3 format. Note: ffmpeg framework is required."""
        if extension == 'mp3':
            return file

        with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as tmp_in:
            file.save(tmp_in.name)
            tmp_in_path = tmp_in.name

        tmp_out_path = tmp_in_path.replace(f".{extension}", ".mp3")

        try:
            FFmpeg(
                inputs={tmp_in_path: None},
                outputs={tmp_out_path: f"-vn -ar 44100 -ac 2 -b:a {bitrate}"}
                # video none - audio rate 44100Hz - audio channel stereo - bitrate (192kbps by default)
            ).run()

            with open(tmp_out_path, 'rb') as f:
                output = io.BytesIO(f.read())
            output.seek(0)
        finally:
            os.remove(tmp_in_path)
            if os.path.exists(tmp_out_path):
                os.remove(tmp_out_path)

        original_name = file.filename.rsplit('.', 1)[0]
        return FileStorage(
            stream=output,
            filename=f"{original_name}.mp3",
            content_type="audio/mpeg"
        )
