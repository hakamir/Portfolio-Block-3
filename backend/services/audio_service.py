from models.artist import Artist, Album, Track


def upsert_track(artist_slug, album_slug, track_src, metadata):
    track_number = metadata['track_number'] if metadata['track_number'] > 0 else 1

    track_obj = Track(
        trackNumber=track_number,
        title=metadata['title'],
        src=track_src,
        tags=metadata.get('tags', [])
    )

    artist = Artist.objects(slug=artist_slug).first()

    if not artist:
        # Complete creation of the artist and album objects, including the track
        album_obj = Album(
            slug=album_slug,
            title=metadata['album'],
            order=1,
            tracks=[track_obj]
        )
        artist = Artist(
            slug=artist_slug,
            title=metadata['artist'],
            order=1,
            albums=[album_obj]
        )
        artist.save()
        return

    # The artist exists, search the album
    album = next((a for a in artist.albums if a.slug == album_slug), None)

    if not album:
        # Create the album object, including the track
        album_obj = Album(
            slug=album_slug,
            title=metadata['album'],
            order=1,
            tracks=[track_obj]
        )
        artist.albums.append(album_obj)
        artist.save()
        return

    # The album exists, search the track
    track_exists = any(t.src == track_src for t in album.tracks)
    if not track_exists:
        album.tracks.append(track_obj)
        artist.save()
