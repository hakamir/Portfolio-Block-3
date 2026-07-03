import os

from flask import current_app
from mutagen.id3 import ID3, ID3NoHeaderError, TPE1, TALB, TRCK, TIT2, TCON


def get_files(folder, tracked_files):
    result = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, folder)
            relative_path = relative_path.replace('\\', '/')
            if relative_path not in tracked_files:
                result.append(relative_path)
    return result


def cleanup_empty_dirs(folder):
    for root, dirs, files in os.walk(folder, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)


def read_id3_tags(filepath: str) -> dict | None:
    try:
        tags = ID3(filepath)
    except ID3NoHeaderError:
        return None

    artist = str(tags.get('TPE1', ''))
    album = str(tags.get('TALB', ''))
    title = str(tags.get('TIT2', ''))
    track_number = str(tags.get('TRCK', '0'))
    track_tags = [t.strip() for t in str(tags.get('TCON', '')).split(',') if t.strip()]
    if not any([artist, album, title]):
        return None

    return {
        'artist': artist,
        'album': album,
        'title': title,
        'track_number': int(track_number) if track_number.isdigit() else 0,
        'tags': track_tags
    }

def write_id3_tags(filepath: str, metadata: dict) -> None:
    try:
        try:
            tags = ID3(filepath)
            tags.delete()
        except ID3NoHeaderError:
            tags = ID3()

        tags[TPE1] = TPE1(encoding=3, text=metadata.get('artist', ''))
        tags[TALB] = TALB(encoding=3, text=metadata.get('album', ''))
        tags[TIT2] = TIT2(encoding=3, text=metadata.get('title', ''))
        tags[TRCK] = TRCK(encoding=3, text=str(metadata.get('track_number', 0)))
        tags[TCON] = TCON(encoding=3)
        tags[TCON].genres = metadata.get('tags', [])
        tags.save(filepath)
    except Exception as e:
        current_app.logger.warning(f"Failed to write ID3 tags to {filepath}: {e}")
