# 🍽️ Recipe Platform API

A RESTful API built with Django and Django REST Framework for a recipe sharing platform. Creators publish and manage recipes, visitors discover and bookmark them, and admins oversee the platform.

---

## 📌 Project Overview

The Recipe Platform allows:
- **Creators** to publish recipes with ingredients, step-by-step instructions, images, prep time, and visibility control
- **Visitors** to browse, search, bookmark, and rate recipes
- **Admins** to manage the platform via the Django admin panel

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.x |
| API | Django REST Framework |
| Auth | JWT via djangorestframework-simplejwt |
| Database | PostgreSQL |
| Containerization | Docker & Docker Compose |
| CI/CD | GitHub Actions |
| Image Handling | Pillow |
| Config | python-decouple |

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.12+
- PostgreSQL (local) or Docker Desktop
- Git

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/recipe-platform.git
cd recipe-platform
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Then open `.env` and fill in your values (see Environment Variables table below).

### 5. Create the database
In PostgreSQL (via psql or pgAdmin):
```sql
CREATE DATABASE recipe_db;
```

### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Create a superuser
```bash
python manage.py createsuperuser
```

### 8. Start the development server
```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/admin/** to access the admin panel.

---

## 🐳 Running with Docker

```bash
# Build and start all services
docker compose up --build

# Run in background
docker compose up -d

# Stop all services
docker compose down
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `your-secret-key-here` |
| `DEBUG` | Debug mode toggle | `True` |
| `DB_NAME` | PostgreSQL database name | `recipe_db` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `yourpassword` |
| `DB_HOST` | Database host | `localhost` or `db` (Docker) |
| `DB_PORT` | Database port | `5432` |
| `DJANGO_SETTINGS_MODULE` | Settings module to use | `recipe_platform.settings.dev` |

---

## 🗺️ API Endpoint Summary

### Auth Endpoints — `/api/auth/`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/auth/register/` | Register a new user | Public |
| POST | `/api/auth/login/` | Login and get JWT tokens | Public |
| POST | `/api/auth/refresh/` | Refresh access token | Public |
| POST | `/api/auth/logout/` | Blacklist refresh token | Authenticated |
| GET/PUT | `/api/auth/profile/` | View or update own profile | Authenticated |

### Tag Endpoints — `/api/`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/api/tags/` | List all tags | Public |
| POST | `/api/tags/` | Create a tag | Authenticated |

### Recipe Endpoints — `/api/`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/api/recipes/` | List all public recipes | Public |
| POST | `/api/recipes/` | Create a new recipe | Creator only |
| GET | `/api/recipes/{id}/` | Get recipe details | Public |
| PUT/PATCH | `/api/recipes/{id}/` | Update a recipe | Recipe author only |
| DELETE | `/api/recipes/{id}/` | Delete a recipe | Recipe author only |

### Ingredients & Steps — nested under `/api/recipes/{id}/`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET/POST | `/api/recipes/{id}/ingredients/` | List or add ingredients | Auth |
| GET/PUT/DELETE | `/api/recipes/{id}/ingredients/{id}/` | Manage one ingredient | Recipe author |
| GET/POST | `/api/recipes/{id}/steps/` | List or add steps | Auth |
| GET/PUT/DELETE | `/api/recipes/{id}/steps/{id}/` | Manage one step | Recipe author |

### Bookmarks

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/recipes/{id}/bookmark/` | Toggle bookmark on/off | Authenticated |
| GET | `/api/bookmarks/` | List own bookmarks | Authenticated |

### Ratings

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET/POST | `/api/recipes/{id}/ratings/` | List or add rating | Auth |
| GET/PUT/DELETE | `/api/recipes/{id}/ratings/{id}/` | Manage own rating | Rating owner |

### Dashboard

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/api/dashboard/` | Creator stats dashboard | Creator only |

---

## 🔍 Search & Filter

The `/api/recipes/` endpoint supports the following query parameters:

| Parameter | Description | Example |
|---|---|---|
| `search` | Search by title, description, or author | `?search=jollof` |
| `tag` | Filter by tag slug | `?tag=nigerian` |
| `cuisine` | Filter by cuisine tag | `?cuisine=italian` |
| `dietary` | Filter by dietary tag | `?dietary=vegan` |
| `max_time` | Filter by max prep time (minutes) | `?max_time=30` |
| `difficulty` | Filter by difficulty level | `?difficulty=easy` |
| `min_rating` | Filter by minimum average rating | `?min_rating=4` |
| `ordering` | Order results | `?ordering=-created_at` |

---

## 👤 User Roles

| Role | Permissions |
|---|---|
| **Creator** | Create, edit, delete own recipes. View own dashboard. |
| **Visitor** | Browse public recipes, bookmark, and rate recipes. |
| **Admin** | Full access via Django admin panel. |

---

## 🧪 Running Tests

```bash
python manage.py test --verbosity=2
```

Expected output:
```
Found 15 tests...
...............
Ran 15 tests in 3.2s
OK
```

---

## 📁 Project Structure

```
recipe-platform/
├── .github/workflows/ci.yml     # GitHub Actions CI/CD
├── recipe_platform/
│   ├── settings/
│   │   ├── base.py              # Shared settings
│   │   ├── dev.py               # Development settings
│   │   └── prod.py              # Production settings
│   └── urls.py
├── accounts/                    # Auth & user management
│   ├── models.py                # Custom User model
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── recipes/                     # Core recipe features
│   ├── models.py                # Recipe, Tag, Ingredient, etc.
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   └── tests.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

---

## 🚀 Deployment

This project is deployed on **Railway**.

Live URL: `https://your-app.railway.app`

---

## 📄 License

This project was built as a Django Bootcamp final project. For educational use.
