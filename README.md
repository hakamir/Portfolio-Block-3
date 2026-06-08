# Artist Portfolio — Block 3: Frameworks

> [!NOTE]
> Part of a 3-block final project series.
> - [Block 1 — Frontend](https://github.com/hakamir/Portfolio-Block-1) (vanilla HTML/CSS/JS)
> - [Block 2 — Backend](https://github.com/hakamir/Portfolio-Block-2) (raw Python)
> - **[Block 3 — Full-stack with frameworks](https://github.com/hakamir/Portfolio-Block-3) (this repo)**

A full-stack portfolio web application for a music artist. Built with **Vue 3** on the frontend and **Flask** on the
backend, with MongoDB as the database.

---

## Features

### Public

- **Home** — Hero section and biography
- **Portfolio** — Browse artists, albums, and tracks with an integrated audio player; full-text search
- **Gallery** — Multi-gallery image viewer with progressive loading
- **Contact** — Rate-limited contact form

### Admin Dashboard (protected)

- **Works** — Full CRUD for artists → albums → tracks; drag-and-drop reordering; audio file upload
- **Gallery** — Full CRUD for galleries and images; image upload (WebP)
- **Biography** — Content editor
- **Messages** — Inbox with read/unread status, trash and bulk actions
- **Settings** — Change password; orphaned gallery and audio cleanup; change background images

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

### [Authentication](#authentication-1)

| Method | Path                                         | Auth | Description       |
|-------:|----------------------------------------------|------|-------------------|
|   POST | [`/api/auth/login`](#post-apiauthlogin)      | —    | Login (5 req/min) |
|   POST | [`/api/auth/logout`](#post-apiauthlogout)    | JWT  | Logout            |
|   POST | [`/api/auth/refresh`](#put-apiauthpassword)  | JWT  | Refresh token     |
|    PUT | [`/api/auth/password`](#post-apiauthrefresh) | JWT  | Change password   |

### [Artists](#artists-1)

| Method | Path                                        | Auth | Description                      |
|-------:|---------------------------------------------|------|----------------------------------|
|    GET | [`/api/artists`](#get-apiartists)           | —    | All artists with albums & tracks |
|    PUT | [`/api/artists`](#put-apiartists)           | JWT  | Create/update artists (bulk)     |
| DELETE | [`/api/artists/<id>`](#delete-apiartistsid) | JWT  | Delete artist                    |

### [Biography](#biography-1)

| Method | Path                                  | Auth | Description       |
|-------:|---------------------------------------|------|-------------------|
|    GET | [`/api/biography`](#get-apibiography) | —    | Biography content |
|    PUT | [`/api/biography`](#put-apibiography) | JWT  | Update biography  |

### [Gallery](#gallery-1)

| Method | Path                                                                 | Auth | Description                      |
|-------:|----------------------------------------------------------------------|------|----------------------------------|
|    GET | [`/api/gallery`](#get-apigallery)                                    | —    | All galleries with images        |
|    PUT | [`/api/gallery`](#put-apigallery)                                    | JWT  | Create/update galleries (bulk)   |
| DELETE | [`/api/gallery/<id>`](#delete-apigalleryid)                          | JWT  | Delete gallery                   |

### [Messages](#messages-1)

| Method | Path                                          | Auth | Description                 |
|-------:|-----------------------------------------------|------|-----------------------------|
|    GET | [`/api/messages`](#get-apimessages)           | JWT  | List messages               |
|   POST | [`/api/messages`](#post-apimessages)          | —    | Submit message (1 req/min)  |
|  PATCH | [`/api/messages/<id>`](#patch-apimessagesid)  | JWT  | Update message (read/trash) |
| DELETE | [`/api/messages/<id>`](#delete-apimessagesid) | JWT  | Delete message              |

### [Uploads](#uploads-1)

| Method | Path                                                  | Auth | Description              |
|-------:|-------------------------------------------------------|------|--------------------------|
|    GET | [`/api/upload/<path>`](#get-apiupload)                | —    | Serve uploaded files     |
|   POST | [`/api/upload/audio`](#post-apiuploadaudio)           | JWT  | Upload audio files       |
|   POST | [`/api/upload/gallery`](#post-apiuploadgallery)       | JWT  | Upload gallery images    |
|   POST | [`/api/upload/background`](#post-apiuploadbackground) | JWT  | Upload background images |

### [Orphaned files management](#orphaned-files)

| Method | Path                                                | Auth | Description                 |
|-------:|-----------------------------------------------------|------|-----------------------------|
|    GET | [`/api/orphans/audio`](#get-apiorphansaudio)        | JWT  | List orphaned audio files   |
| DELETE | [`/api/orphans/audio`](#delete-apiorphansaudio)     | JWT  | Delete orphaned audio files |
|    GET | [`/api/orphans/gallery`](#get-apiorphansgallery)    | JWT  | List orphaned image files   |
| DELETE | [`/api/orphans/gallery`](#delete-apiorphansgallery) | JWT  | Delete orphaned image files |

---

## Getting Started

### Option A — Docker (recommended)

**1. Configure environment**

```bash
cp .env.example .env
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

> [!NOTE]
> FFmpeg is not required for the backend to run, but is required for the audio conversion feature. It is still
> possible to upload and play audio files in `.mp3` format.

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

> [!NOTE]
> `.env.development` is gitignored and only required for Option B (local dev without Docker). In Docker, `VITE_API_URL` is passed as a build argument.

```bash
echo "VITE_API_URL=http://localhost:5000" > .env.development
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

Flask Limiter creates two additional collections automatically: `counter` and `windows`, used to store rate-limits by IP
address.

---

## API Endpoints (detailed)

### Authentication

<sub>[← Back to summary](#api-endpoints)</sub>

## `POST /api/auth/login`

Rate-limited to **5 req/min** by default. No authentication required.

**Request body:**

```json
{
  "email": "admin@example.com",
  "pwd": "<Your Password>"
}
```

**Response `200`:**

```json
{
  "token": "<JWT access token>"
}
```

**Errors:** `400` missing credentials - `401` invalid credentials

## `POST /api/auth/logout`

Unset JWT cookies from the client's browser, logging the user out.

**Request body:**

- None

**Response `200`:**

```json
{
  "logged_out": true
}
```

## `PUT /api/auth/password`

Rate-limited to **1 req/min** by default. Authentication required.

Rate limit is present to avoid brute-force attacks if JWT is compromised.

**Request body:**

```json
{
  "currentPwd": "Curr3n!_P@ssw0rd",
  "newPwd": "N3w!_P@ssw0rd12+3="
}
```

**Response `200`:**

```json
{
  "updated": true
}
```

**Errors:** `400` validation errors - `401` invalid credentials

## `POST /api/auth/refresh`

Creates a new access token using a valid refresh token.

**Request body:**

- None

**Response `200`:**

```json
{
  "token": "<new JWT access token>"
}
```

**Errors:** `401` No refresh token found / expired - `422` Malformed/Wrong refresh token / invalid signature

---

### Artists

<sub>[← Back to summary](#api-endpoints)</sub>

## `GET /api/artists`

Returns all artists with albums and tracks. No authentication required.

**Response `200`:**

```json
[
  {
    "_id": {
      "$oid": "69d7994ec52a15fb197c2908"
    },
    "slug": "artist_1",
    "title": "Artist 1",
    "order": 1,
    "albums": [
      {
        "slug": "album_1",
        "title": "Album 1",
        "order": 1,
        "tracks": [
          {
            "trackNumber": 1,
            "title": "Track 1",
            "src": "track_1.mp3",
            "tags": [
              "tag1",
              "tag2",
              "tag4"
            ]
          },
          {
            "trackNumber": 2,
            "title": "Track 2",
            "src": "track_2.mp3",
            "tags": [
              "tag1",
              "tag3"
            ]
          }
        ]
      },
      {
        "slug": "album_2",
        "title": "Album 2",
        "order": 2,
        "tracks": [
          {
            "trackNumber": 1,
            "title": "Track 1",
            "src": "track_1.mp3",
            "tags": [
              "tag1",
              "tag4"
            ]
          },
          {
            "trackNumber": 2,
            "title": "Track 2",
            "src": "track_2.mp3",
            "tags": [
              "tag1",
              "tag3"
            ]
          },
          {
            "trackNumber": 3,
            "title": "Track 3",
            "src": "track_3.mp3",
            "tags": [
              "tag4"
            ]
          }
        ]
      }
    ]
  }
]
```

## `PUT /api/artists`

Applicative bulk upsert: Processes a list of artists. Each entry is validated, then either updated (if an ID is
provided) or
created, including nested albums and tracks. JWT required.
New artists have an empty `_id` field. Existing artists update their corresponding documents by ID. Raise `404` if given
`id` does not exist.

**Request body:** Follow the structure of the `GET /api/artists` response.

**Response `200`:**

```json
{
  "updated": true
}
```

**Error** `400`: List expected/Validation error- `401` Unauthorized - `404` Artist not found - `415`: Invalid
content-type (JSON expected)

## `DELETE /api/artists/<id>`

Removes an artist and all associated albums and tracks by `id`. JWT required.

**Response `200`:**

```json
{
  "deleted": true
}
```

**Error** `400`: Invalid ID - `401` Unauthorized - `404` Artist not found

This method does not delete the actual audios from the `uploads/audio/` folder. After artist removal, all associated
albums and tracks become [orphans](#get-apiorphansaudio).

---

### Biography

<sub>[← Back to summary](#api-endpoints)</sub>

## `GET /api/biography`

Returns the biography structure, including the main title, associated image URL, and sections with paragraphs.
The biography is stored as a singleton document. No authentication required.

**Response `200`:**

```json
{
  "biography": {
    "_id": "3e5f65c9500d4440b1ad7c4c3103bf19",
    "title": "Biography",
    "image": {
      "sm": "/biography/biography-1-512.webp",
      "md": "/biography/biography-1-1024.webp",
      "lg": "/biography/biography-1-2048.webp"
    },
    "updated_at": "2026-05-19 14:35:17",
    "sections": [
      {
        "title": "Section Title",
        "paragraphs": [
          "Example paragraph"
        ]
      }
    ]
  }
}
```

**Error** `404`: No biography entry found, caused when the seeder was not run.

## `PUT /api/biography`

Updates the biography. The whole structure is required. JWT required.

**Request body:**

```json
{
  "biography": {
    "_id": "b3f435dc399b11f1a3ca244bfe4c7954",
    "title": "Who am I?",
    "image": {
      "sm": "/biography/biography-1-512.webp",
      "md": "/biography/biography-1-1024.webp",
      "lg": "/biography/biography-1-2048.webp"
    },
    "updated_at": "2026-05-19 14:49:19",
    "sections": [
      {
        "title": "Background & Musical Foundation",
        "paragraphs": [
          "I am a professional guitarist and composer...",
          "Formally trained in contemporary music and jazz..."
        ]
      }
    ]
  }
}
```

**Response `200`:** Updated biography object (same shape as GET).

**Errors:** `400` malformed body - `401` missing/invalid token

---

### Gallery

<sub>[← Back to summary](#api-endpoints)</sub>

## `GET /api/gallery`

Returns all galleries with associated image metadata and URL. No authentication required.

**Response `200`:**

```json
[
  {
    "_id": {
      "$oid": "69db8e78a650f456163ba186"
    },
    "images": [
      {
        "src": "gallery_1_a296a2f6-5ff9-4e49-bd5a-23d16b34b863.webp",
        "title": "Image 1 title",
        "location": "Somewhere",
        "date": {
          "$date": "2025-11-14T00:00:00.000Z"
        },
        "order": 1,
        "alt": "Image 1 title, Somewhere, 2025"
      },
      {
        "src": "gallery_1_a296a2f6-5ff9-4e49-bd5a-23d16b34b863.webp",
        "title": "Image 2 title",
        "location": "Somewhere else",
        "date": {
          "$date": "2024-04-29T00:00:00.000Z"
        },
        "order": 2,
        "alt": "Image 2 title, Somewhere else, 2024"
      }
    ],
    "order": 1,
    "slug": "gallery_1",
    "title": "Gallery 1"
  }
]
```

## `PUT /api/gallery`

Applicative bulk upsert: Processes a list of galleries. Each entry is validated, then either updated (if an ID is
provided) or
created, including nested images. JWT required.
New galleries have an empty `_id` field. Existing galleries update their corresponding documents by ID. Raise `404` if
given
`id` does not exist.

**Request body:** Follow the structure of the `GET /api/gallery` response.

**Response `200`:**

```json
{
  "updated": true
}
```

**Error** `400`: List expected/Validation error- `401` Unauthorized - `404` Gallery not found - `415`: Invalid
content-type (JSON expected)

## `DELETE /api/gallery/<id>`

Removes a gallery and images meta by `id`. JWT required.

This method does not delete the actual images from the `uploads/gallery/` folder. After gallery removal, all associated
images become [orphans](#get-apiorphansgallery).

**Response `200`:**

```json
{
  "deleted": true
}
```

**Error** `400`: Invalid ID - `401` Unauthorized - `404` Gallery not found

---

### Messages

<sub>[← Back to summary](#api-endpoints)</sub>

## `GET /api/messages`

Returns a list of all messages. JWT Required.

**Response `200`:**

```json
[
  {
    "name": "Jake Thompson",
    "email": "jake.thompson@gmail.com",
    "message": "Hi, I discovered your portfolio...",
    "date": "2026-04-07 22:45:34",
    "read": true,
    "trashed": true,
    "_id": "1"
  },
  {
    "name": "Emily Carter",
    "email": "emily.carter@musiclive.com",
    "message": "Hello, I'm organizing a live...",
    "date": "2026-01-16 18:32:45",
    "read": false,
    "trashed": false,
    "_id": "2"
  }
]
```

Respond with an empty array if no messages are found.

## `POST /api/messages`

Create a new message. Rate-limited to **1 req/min** by default. No authentication required.

**Request body:**

```json
{
  "name": "Test",
  "email": "test@test.com",
  "message": "test"
}
```

**Response `201`:**

```json
{
  "message": "Message created successfully"
}
```

**Errors:** `400` missing fields - `429` rate limit exceeded

Missing fields response example:

```json
{
  "error": "Missing required fields: email, message"
}
```

Look to [`GET /api/messages`](#get-apimessages) response to see the final data structure after the controller job.

## `PATCH /api/messages/<id>`

Marks a message as read, trashed, or replied. JWT required.

**Request body** (one or multiple fields):

```json
{
  "is_read": true,
  "is_trashed": false,
  "is_replied": false
}
```

**Response `200`:** Updated message object.

**Errors:** `400` malformed body · `401` unauthorized · `404` not found

## `DELETE /api/messages/<id>`

Permanently deletes a message. JWT required.

**Response `200`:**

```json
{
  "message": "Message deleted successfully"
}
```

**Errors:** `400` Invalid fields / type error / invalid request body - `401` unauthorized - `404` not found

---

### Uploads

<sub>[← Back to summary](#api-endpoints)</sub>

## `GET /api/upload/*`

Serves files from the `uploads/` directory (backgrounds, audio, and gallery). No authentication required.

Example: `GET /api/upload/background/hero/hero-512.wepb`

## `POST /api/upload/audio`

Uploads audio files. JWT required.

```formdata
file: <file> [Content-Disposition: form-data; name="file"; filename="<filename>.ext" Content-Type: audio/*]
artistSlug: artist_slug
albumSlug: album_slug
trackSrc: track_slug.ext
```

**Response `201`:**

```json
{
  "uploaded": true
}
```

**Errors:** `400` No file part/missing required field - `415` Invalid mime type/Invalid file type - `500` Conversion
failed

## `POST /api/upload/gallery`

Uploads gallery images. JWT required.

```formdata
file: <file> Content-Disposition: form-data; name="file"; filename="<filename>.ext" Content-Type: image/*
gallerySlug: gallery_slug
imageSrc: gallery_gallery_1_a296a2f6-5ff9-4e49-bd5a-23d16b34b863.webp
```

**Response `201`:**

```json
{
  "uploaded": true
}
```

**Errors:** `400` No file part/missing required field - `415` Invalid mime type/Invalid file type

## `POST /api/upload/background`

Uploads background images. JWT required.

```formdata
file: <file_2048> Content-Disposition: form-data; name="file"; filename="<filename>.ext" Content-Type: image/*
file: <file_1024> Content-Disposition: form-data; name="file"; filename="<filename>.ext" Content-Type: image/*
file: <file_512> Content-Disposition: form-data; name="file"; filename="<filename>.ext" Content-Type: image/*
destination: <destination> (hero | portfolio | biography)
```

**Response `201`:**

```json
{
  "uploaded": true
}
```

**Errors:** `400` Invalid destination/missing required field/Invalid file

---

### Orphaned files

<sub>[← Back to summary](#api-endpoints)</sub>

## `GET /api/orphans/audio`

Returns a list of audio files that are not associated with any artist. JWT required.

## `DELETE /api/orphans/audio`

Deletes selected orphaned audio files. JWT required.

**Request body**:

```json
{
  "files": [
    "artist/album/track1.mp3",
    "artist/album/track2.mp3",
    "artist/album/track3.mp3"
  ]
}
```

**Response `200`:**

```json
{
  "deleted": true
}
```

**Errors:** `401` unauthorized

## `GET /api/orphans/gallery`

Returns a list of image files that are not associated with any gallery. JWT required.

## `DELETE /api/orphans/gallery`

Deletes all orphaned image files. JWT required.

```json
{
  "files": [
    "gallery/gallery_0001.webp",
    "gallery/gallery_0002.webp",
    "gallery/gallery_0003.webp"
  ]
}
```

**Response `200`:**

```json
{
  "deleted": true
}
```

**Errors:** `401` unauthorized
