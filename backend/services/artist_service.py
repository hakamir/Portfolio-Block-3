import os
from datetime import datetime, timezone
from uuid import uuid4

from models.artist import Album, Track
from models.orphan_audio import OrphanAudio
from utils.filesystem import write_id3_tags


def orphan_removed_tracks(user, artist, payload_albums, upload_folder):
    """Create Orphan documents for albums and tracks removed from the payload."""
    now = datetime.now(timezone.utc)
    payload_album_slugs = {al.slug for al in payload_albums if al.slug}

    for existing_album in artist.albums:
        if existing_album.slug not in payload_album_slugs:
            for track in existing_album.tracks:
                _orphan_if_file_exists(user, artist, existing_album, track, upload_folder, now)
        else:
            payload_album = next(al for al in payload_albums if al.slug == existing_album.slug)
            payload_srcs = {t.src for t in payload_album.tracks if t.src}
            for track in existing_album.tracks:
                if track.src not in payload_srcs:
                    _orphan_if_file_exists(user, artist, existing_album, track, upload_folder, now)


def orphan_all_tracks(user, artist, upload_folder):
    """Create Orphan documents for every track in an artist (used before deletion)."""
    now = datetime.now(timezone.utc)
    for album in artist.albums:
        for track in album.tracks:
            _orphan_if_file_exists(user, artist, album, track, upload_folder, now, artist_id=None)


def _orphan_if_file_exists(user, artist, album, track, upload_folder, now, artist_id=...):
    file_path = os.path.join(upload_folder, 'audio', artist.slug, album.slug, track.src)
    if not os.path.exists(file_path):
        return
    OrphanAudio(
        user=user,
        artist_id=artist.id if artist_id is ... else artist_id,
        artist_slug=artist.slug,
        artist_title=artist.title,
        album_slug=album.slug,
        album_title=album.title,
        track_title=track.title,
        track_number=track.trackNumber,
        track_src=track.src,
        tags=list(track.tags),
        deleted_at=now,
    ).save()


def build_albums(payload_albums, existing_artist=None):
    """Build Album/Track objects with UUID slug/src resolution."""
    existing_album_map = {a.slug: a for a in existing_artist.albums} if existing_artist else {}

    albums = []
    for album in payload_albums:
        if album.slug and album.slug in existing_album_map:
            album_slug = album.slug
            existing_tracks = {t.src for t in existing_album_map[album.slug].tracks}
        else:
            album_slug = str(uuid4())
            existing_tracks = set()

        tracks = [
            Track(
                trackNumber=t.trackNumber,
                title=t.title,
                src=t.src if (t.src and t.src in existing_tracks) else str(uuid4()) + '.mp3',
                tags=t.tags,
            )
            for t in album.tracks
        ]

        albums.append(Album(slug=album_slug, title=album.title, order=album.order, tracks=tracks))

    return albums


def sync_id3_tags(artist, upload_folder):
    """Write ID3 tags on all physical files that already exist."""
    for album in artist.albums:
        for track in album.tracks:
            file_path = os.path.join(upload_folder, 'audio', artist.slug, album.slug, track.src)
            if os.path.exists(file_path):
                write_id3_tags(file_path, {
                    'artist': artist.title,
                    'album': album.title,
                    'title': track.title,
                    'track_number': str(track.trackNumber),
                    'tags': ','.join(track.tags),
                })
