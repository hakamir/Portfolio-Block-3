import os
from datetime import datetime, timezone
from uuid import uuid4

from models.gallery import Gallery, GalleryImage
from models.orphan_gallery import OrphanGallery


def orphan_removed_images(user, gallery, payload_images, upload_folder):
    """Create OrphanGallery documents for images removed from the payload."""
    now = datetime.now(timezone.utc)
    payload_srcs = {img.src for img in payload_images if img.src}

    for existing_image in gallery.images:
        if existing_image.src not in payload_srcs:
            _orphan_if_file_exists(user, gallery, existing_image, upload_folder, now)


def orphan_all_images(user, gallery, upload_folder):
    """Create OrphanGallery documents for every image in a gallery (used before deletion)."""
    now = datetime.now(timezone.utc)
    for image in gallery.images:
        _orphan_if_file_exists(user, gallery, image, upload_folder, now)


def _orphan_if_file_exists(user, gallery, image, upload_folder, now):
    file_path = os.path.join(upload_folder, 'gallery', gallery.slug, image.src)
    if not os.path.exists(file_path):
        return
    OrphanGallery(
        user=user,
        gallery_slug=gallery.slug,
        gallery_title=gallery.title,
        image_src=image.src,
        image_title=image.title,
        image_location=image.location,
        image_date=image.date,
        image_alt=image.alt,
        image_order=image.order,
        deleted_at=now,
    ).save()


def build_images(payload_images, existing_gallery=None):
    """Build GalleryImage objects with UUID src resolution for new images."""
    existing_srcs = {img.src for img in existing_gallery.images} if existing_gallery else set()
    return [
        GalleryImage(
            src=img.src if (img.src and img.src in existing_srcs) else str(uuid4()) + '.webp',
            title=img.title,
            location=img.location,
            date=img.date,
            order=img.order,
            alt=img.alt,
        )
        for img in payload_images
    ]


def upsert_image(user, gallery_slug, image_src, metadata):
    """Insert an image into its gallery, creating the gallery if it doesn't exist."""
    image_obj = GalleryImage(
        src=image_src,
        title=metadata['title'],
        location=metadata.get('location', ''),
        date=metadata.get('date'),
        alt=metadata.get('alt', ''),
        order=metadata.get('order', 1),
    )

    gallery = Gallery.objects(slug=gallery_slug, user=user).first()

    if not gallery:
        Gallery(
            user=user,
            slug=gallery_slug,
            title=metadata['gallery_title'],
            order=1,
            images=[image_obj],
        ).save()
        return

    if not any(img.src == image_src for img in gallery.images):
        gallery.images.append(image_obj)
        gallery.save()
