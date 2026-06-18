import os

from mutagen.id3 import ID3, ID3NoHeaderError


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


def read_id3_metadata(filepath: str) -> dict | None:
    try:
        tags = ID3(filepath)
    except ID3NoHeaderError:
        return None

    artist = str(tags.get('TPE1', ''))
    album = str(tags.get('TALB', ''))
    title = str(tags.get('TIT2', ''))
    track_number = str(tags.get('TRCK', '0'))

    if not any([artist, album, title]):
        return None

    return {
        'artist': artist,
        'album': album,
        'title': title,
        'track_number': int(track_number) if track_number.isdigit() else 0
    }
