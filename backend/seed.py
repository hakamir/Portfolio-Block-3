import os
import bcrypt
from urllib.parse import quote_plus
from mongoengine import connect

from models.gallery import Gallery, GalleryImage
from models.user import User
from models.biography import Biography, ImageSize, Section


def get_uri():
    user = os.environ['MONGODB_USER']
    password = quote_plus(os.environ['MONGODB_PASSWORD'])
    host = os.environ.get('MONGODB_HOST', 'mongodb')
    port = os.environ.get('MONGODB_PORT', '27017')
    db = os.environ.get('MONGODB_DATABASE', 'Portfolio')
    timeout = os.environ.get('MONGODB_TIMEOUT', '5000')
    return f"mongodb://{user}:{password}@{host}:{port}/{db}?authSource={db}&serverSelectionTimeoutMS={timeout}"


def seed_user():
    email = os.environ.get('TEST_USER_EMAIL')
    password = os.environ.get('TEST_USER_PASSWORD')

    if not email or not password:
        print("TEST_USER_EMAIL or TEST_USER_PASSWORD not set — skipping user seed")
        return

    if User.objects(email=email).first():
        print(f"User '{email}' already exists — skipping")
        return

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
    User(email=email, password=hashed.decode('utf-8')).save()
    print(f"Created user: {email}")


def seed_biography():
    if Biography.objects.first():
        print("Biography already exists — skipping")
        return

    Biography(
        title="Biography",
        image=ImageSize(
            sm="/biography/biography-1-512.webp",
            md="/biography/biography-1-1024.webp",
            lg="/biography/biography-1-2048.webp",
        ),
        sections=[
            Section(title="Section Title", paragraphs=["Example paragraph"])
        ],
    ).save()
    print("Created biography")


def seed():
    connect(host=get_uri())
    seed_user()
    seed_biography()


if __name__ == '__main__':
    seed()
