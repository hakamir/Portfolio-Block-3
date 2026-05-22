# Artist Portfolio — Block 3: Frameworks

> [!NOTE]
> Part of a 3-block final project series.
> - [Block 1 — Frontend](https://github.com/hakamir/Portfolio-Block-1) (vanilla HTML/CSS/JS)
> - [Block 2 — Backend](https://github.com/hakamir/Portfolio-Block-2) (raw Python)
> - **[Block 3 — Full-stack with frameworks](https://github.com/hakamir/Portfolio-Block-3) (this repo)**

A full-stack portfolio web application for a music artist. Built with **Vue 3** on the frontend and **Flask** on the backend, with MongoDB as the database.

---

## Features

### Public

- **Home** — Hero section and biography
- **Portfolio** — Browse artists, albums and tracks with an integrated audio player; full-text search
- **Gallery** — Multi-gallery image viewer with progressive loading
- **Contact** — Rate-limited contact form

### Admin Dashboard (protected)

- **Works** — Full CRUD for artists → albums → tracks; drag-and-drop reordering; audio file upload
- **Gallery** — Full CRUD for galleries and images; image upload (WebP)
- **Biography** — Content editor
- **Messages** — Inbox with read/unread status, trash and bulk actions
- **Settings** — Change password; orphaned file cleanup

---

## Tech Stack

| Layer                  | Technology                                          |
|------------------------|-----------------------------------------------------|
| **Frontend framework** | Vue 3 · Composition API · `<script setup>`          |
| **Build tool**         | Vite 8                                              |
| **Language**           | TypeScript                                          |
| **State management**   | Pinia                                               |
| **Routing**            | Vue Router 4                                        |
| **Styling**            | Tailwind CSS 4.2                                    |
| **HTTP client**        | Axios (JWT interceptors)                            |
| **Backend framework**  | Flask                                               |
| **Database**           | MongoDB (MongoEngine ODM)                           |
| **Authentication**     | Flask-JWT-Extended (15 min access / 30 day refresh) |
| **Password hashing**   | bcrypt                                              |
| **Rate limiting**      | Flask-Limiter                                       |
| **Containerisation**   | Docker · Docker Compose · Nginx                     |

---

## API Endpoints

All routes are prefixed with `/api`.

### Authentication
| Method | Path                 | Auth | Description       |
|-------:|----------------------|------|-------------------|
|   POST | `/api/auth/login`    | —    | Login (5 req/min) |
|   POST | `/api/auth/logout`   | JWT  | Logout            |
|   POST | `/api/auth/refresh`  | JWT  | Refresh token     |
|    PUT | `/api/auth/password` | JWT  | Change password   |

### Artists
| Method | Path                | Auth | Description                      |
|-------:|---------------------|------|----------------------------------|
|    GET | `/api/artists`      | —    | All artists with albums & tracks |
|    PUT | `/api/artists`      | JWT  | Create/update artists (bulk)     |
| DELETE | `/api/artists/<id>` | JWT  | Delete artist                    |

### Biography
| Method | Path             | Auth | Description       |
|-------:|------------------|------|-------------------|
|    GET | `/api/biography` | —    | Biography content |
|    PUT | `/api/biography` | JWT  | Update biography  |

### Gallery
| Method | Path                  | Auth | Description                    |
|-------:|-----------------------|------|--------------------------------|
|    GET | `/api/gallery`        | —    | All galleries with images      |
|    PUT | `/api/gallery`        | JWT  | Create/update galleries (bulk) |
| DELETE | `/api/gallery/<id>`   | JWT  | Delete gallery                 |

### Messages
| Method | Path                 | Auth | Description                 |
|-------:|----------------------|------|-----------------------------|
|    GET | `/api/messages`      | JWT  | List messages               |
|   POST | `/api/messages`      | —    | Submit message (1 req/min)  |
|  PATCH | `/api/messages/<id>` | JWT  | Update message (read/trash) |
| DELETE | `/api/messages/<id>` | JWT  | Delete message              |

### Uploads
| Method | Path                  | Auth | Description         |
|-------:|-----------------------|------|---------------------|
|   POST | `/api/upload/audio`   | JWT  | Upload audio file   |
|   POST | `/api/upload/gallery` | JWT  | Upload image        |
|    GET | `/api/upload/<path>` | —    | Serve uploaded file |

### Orphaned files management
| Method | Path                   | Auth | Description                 |
|-------:|------------------------|------|-----------------------------|
|    GET | `/api/orphans/audio`   | JWT  | List orphaned audio files   |
| DELETE | `/api/orphans/audio`   | JWT  | Delete orphaned audio files |
|    GET | `/api/orphans/gallery` | JWT  | List orphaned image files   |
| DELETE | `/api/orphans/gallery` | JWT  | Delete orphaned image files |

---

## Getting Started

### Option A — Docker (recommended)

**1. Configure environment**

```bash
cp .env.docker.example .env
```

Fill in `.env`:

```env
MONGO_ROOT_USER=root
MONGO_ROOT_PASSWORD=your_root_password
MONGODB_USER=portfolio
MONGODB_PASSWORD=your_db_password
JWT_SECRET_KEY=your_long_random_secret
TEST_USER_EMAIL=admin@example.com
TEST_USER_PASSWORD=your_admin_password
```

**2. Start all services**

```bash
docker compose up --build
```

This runs four services:

|  Service   | URL                   | Description                        |
|:----------:|-----------------------|------------------------------------|
| `frontend` | http://localhost      | Vue app (Vite dev server)          |
| `backend`  | http://localhost:5000 | Flask API                          |
| `mongodb`  | localhost:27018       | MongoDB (host access)              |
|  `seeder`  | —                     | Creates test user + biography data |

On the first run, the seeder automatically creates:
- An admin user with the email/password from `.env`
- A default biography document

**3. Useful commands**

```bash
docker compose down          # stop (data preserved)
docker compose down -v       # stop + wipe database
docker compose logs backend  # view backend logs
docker compose cp backend/uploads/. backend:/app/uploads/  # restore local uploads
```

**Connect to MongoDB via Compass (dev only):**
```
mongodb://root:<MONGO_ROOT_PASSWORD>@localhost:27018/?authSource=admin
```
Or :
```
mongodb://<MONGODB_USER>:<MONGO_PASSWORD>@localhost:27018/?authSource=admin
```

### Production

```bash
docker compose -f docker-compose.yml -f docker-compose-prod.yml up --build
```

Both `docker-compose.yml` and `docker-compose.prod.yml` should be specified for the production build.

---

### Option B — Local development

#### Prerequisites

Node.js ≥ 18, Python ≥ 3.14, MongoDB running on `localhost:27017`

#### FFmpeg (required for audio conversion)

Audio files uploaded in formats other than `.mp3` are automatically converted server-side via FFmpeg.

**Supported audio formats:** `mp3` `wma` `aac` `flac` `ogg` `wav` `aiff` `alac` `amr` `m4a`

**macOS**
```bash
brew install ffmpeg
```

**Ubuntu / Debian**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows**
1. Download the latest build from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the archive and add the `bin/` folder to your `PATH`
3. Verify: `ffmpeg -version`

**Backend**

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
pip install -r backend/requirements.txt
cd backend && flask run --debug
```

The API will be available at `http://localhost:5000`.

**Frontend**

```bash
cp .env.example .env.development
# set VITE_API_URL=http://localhost:5000
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## Database

MongoDB collections, created automatically on first Docker startup:

| Collection  | Description                                    |
|-------------|------------------------------------------------|
| `users`     | Admin account (email + bcrypt-hashed password) |
| `artists`   | Nested document: artist → album → tracks       |
| `galleries` | Nested document: gallery → images              |
| `biography` | Single document                                |
| `messages`  | Contact form submissions                       |

Flask Limiter creates two additional collections automatically: `counter` and `windows`, used to store rate-limits by IP address.