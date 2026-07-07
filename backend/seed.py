import os
import bcrypt
from urllib.parse import quote_plus
from mongoengine import connect

from models.user import User
from models.biography import Biography, ImageSize, Section
import dotenv

dotenv.load_dotenv()

user_type = ('artist', 'admin')

def get_uri():
    user = os.environ.get('MONGODB_USER')
    password = quote_plus(os.environ.get('MONGODB_PASSWORD'))
    host = os.environ.get('MONGODB_HOST', 'localhost')
    port = os.environ.get('MONGODB_PORT', '27017')
    db = os.environ.get('MONGODB_DATABASE', 'Portfolio')
    timeout = os.environ.get('MONGODB_TIMEOUT', '5000')
    return f"mongodb://{user}:{password}@{host}:{port}/{db}?authSource={db}&serverSelectionTimeoutMS={timeout}"


def seed_user(user_role: str = 'artist', is_active: bool = False):
    if user_role not in user_type:
        raise ValueError(f"Invalid user type: {user_role}")
    if user_role == 'artist':
        email = os.environ.get('TEST_USER_EMAIL')
        password = os.environ.get('TEST_USER_PASSWORD')
    else:
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')

    if not email or not password:
        print(f"[{user_role.upper()}] email or password not set — skipping user seed")
        return

    if User.objects(email=email).first():
        print(f"User '{email}' already exists — skipping")
        return

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
    User(email=email, password=hashed.decode('utf-8'), role=user_role, is_active=is_active).save()
    print(f"Created user: {email}")


def seed_biography():
    if Biography.objects.first():
        print("Biography already exists — skipping")
        return
    artist = User.objects(role='artist', is_active=True).first()
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
        user=artist
    ).save()
    print("Created biography")


def seed():
    connect(host=get_uri())
    seed_user(user_role='artist', is_active=True)
    seed_user(user_role='admin', is_active=False)
    seed_biography()


if __name__ == '__main__':
    seed()
