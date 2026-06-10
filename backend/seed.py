import os
import bcrypt
from urllib.parse import quote_plus
from mongoengine import connect
from pymongo import MongoClient

from models.user import User
from models.biography import Biography, ImageSize, Section
import dotenv

dotenv.load_dotenv()


def get_uri():
    user = os.environ.get('MONGODB_USER')
    password = quote_plus(os.environ.get('MONGODB_PASSWORD'))
    host = os.environ.get('MONGODB_HOST', 'localhost')
    port = os.environ.get('MONGODB_PORT', '27017')
    db = os.environ.get('MONGODB_DATABASE', 'Portfolio')
    timeout = os.environ.get('MONGODB_TIMEOUT', '5000')
    return f"mongodb://{user}:{password}@{host}:{port}/{db}?authSource={db}&serverSelectionTimeoutMS={timeout}"


def get_admin_client():
    print(os.environ.get('MONGO_ROOT_USER'), os.environ.get('MONGO_ROOT_PASSWORD'))
    admin_user = quote_plus(os.environ.get('MONGO_ROOT_USER'))
    admin_pass = quote_plus(os.environ.get('MONGO_ROOT_PASSWORD'))
    host = os.environ.get('MONGODB_HOST', 'localhost')
    port = os.environ.get('MONGODB_PORT', '27017')
    timeout = int(os.environ.get('MONGODB_TIMEOUT', '5000'))
    client = MongoClient(
        f"mongodb://{admin_user}:{admin_pass}@{host}:{port}/admin?serverSelectionTimeoutMS={timeout}"
    )
    return client


def seed_mongo_user():
    db_name = os.environ.get('MONGODB_DATABASE', 'Portfolio')
    app_user = os.environ.get('MONGODB_USER')
    app_pass = os.environ.get('MONGODB_PASSWORD')

    if not app_user or not app_pass:
        raise ValueError("MONGODB_USER or MONGODB_PASSWORD not set")

    client = get_admin_client()
    db = client[db_name]

    existing = db.command("usersInfo", app_user)
    if existing['users']:
        print(f"MongoDB user '{app_user}' already exists — skipping")
        client.close()
        return

    db.command("createUser", app_user, pwd=app_pass, roles=[{"role": "readWrite", "db": db_name}])
    print(f"Utilisateur MongoDB '{app_user}' créé")
    client.close()


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
    seed_mongo_user()
    connect(host=get_uri())
    seed_user()
    seed_biography()


if __name__ == '__main__':
    seed()
