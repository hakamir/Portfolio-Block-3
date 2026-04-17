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

| Layer | Technology |
|---|---|
| **Frontend framework** | Vue 3 · Composition API · `<script setup>` |
| **Build tool** | Vite 8 |
| **Language** | TypeScript |
| **State management** | Pinia |
| **Routing** | Vue Router 4 |
| **Styling** | Tailwind CSS 4.2 |
| **HTTP client** | Axios (JWT interceptors) |
| **Backend framework** | Flask |
| **Database** | MongoDB (PyMongo / Flask-PyMongo) |
| **Authentication** | Flask-JWT-Extended (8 h tokens) |
| **Password hashing** | bcrypt |
| **Rate limiting** | Flask-Limiter |

---

## API Endpoints

### Authentication
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | — | Login (5 req/min) |
| PUT | `/auth/password` | JWT | Change password |

### Artists
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/artists` | — | All artists with albums & tracks |
| PUT | `/artists` | JWT | Create/update artists (bulk) |
| DELETE | `/artists/<id>` | JWT | Delete artist |

### Biography
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/biography` | — | Biography content |
| PUT | `/biography` | JWT | Update biography |

### Gallery
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/gallery` | — | All galleries with images |
| PUT | `/gallery` | JWT | Create/update galleries (bulk) |
| DELETE | `/gallery/<id>` | JWT | Delete gallery |
| POST | `/gallery/upload` | JWT | Upload image |

### Messages
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/messages` | JWT | List messages |
| POST | `/messages` | — | Submit message (1 req/min) |
| PATCH | `/messages/<id>` | JWT | Update message (read/trash) |
| DELETE | `/messages/<id>` | JWT | Delete message |

### Uploads
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/audio/upload` | JWT | Upload audio file |
| GET | `/uploads/<path>` | — | Serve uploaded file |

### Orphaned files management
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/audio/orphans` | JWT | List orphaned audio files |
| DELETE | `/audio/orphans` | JWT | Delete orphaned audio files |

---

## Getting Started

### Prerequisites

- Node.js ≥ 18
- Python ≥ 3.10
- MongoDB running on `localhost:27017`

### Environment


Copy `.env.example` to `.env` and fill in the values:

```env
VITE_API_URL=http://localhost:5000
JWT_SECRET_KEY=your_secret_key
```

### Backend

```backend
cd backend
python -m venv ../.venv
source ../.venv/Scripts/activate   # Windows: ..\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
The API will be available at `http://localhost:5000`.

### Frontend
```frontend
npm install
npm run dev
```
The app will be available at `http://localhost:5173`.

---

## Database
MongoDB is used with the following collections:
- `users` - Admin account (email + bcrypt password)
- `artists` - nested document: artist -> album -> tracks
- `galleries` - nested document: gallery -> images
- `biography` - single document
- `messages` - contact from submissions
