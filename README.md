# Pulse

Pulse is a full-stack fleet and worker management platform that automates service reminders via SMS. Managers can track workers, assign vehicles, schedule maintenance reminders, and interact with an AI assistant — all from a single dashboard.

---

## Features

- **Worker Management** — Add, edit, and deactivate workers with roles and contact info
- **Vehicle Management** — Assign vehicles to workers and track make, model, year, and plate
- **Automated Reminders** — Schedule service reminders (oil changes, inspections, etc.) delivered via SMS through Twilio
- **Background Task Queue** — Celery + Redis handles asynchronous reminder delivery and scheduled jobs
- **AI Chat Assistant** — Built-in chat powered by OpenAI for quick operational Q&A
- **Dashboard & Metrics** — Visual charts and summary stats built with Recharts
- **JWT Authentication** — Secure login with token-based auth for all API routes

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, Recharts |
| Backend | Flask, SQLAlchemy, Flask-CORS, PyJWT |
| Database | PostgreSQL |
| Task Queue | Celery, Redis |
| SMS | Twilio |
| AI | OpenAI API |
| Containers | Docker, Docker Compose |

---

## Project Structure

```
Pulse/
├── backend/
│   ├── app.py              # Flask app factory, CORS, blueprint registration
│   ├── config.py           # Environment variable loading
│   ├── database.py         # DB setup
│   ├── tasks.py            # Celery tasks (reminder delivery)
│   ├── models/
│   │   ├── user.py
│   │   ├── worker.py
│   │   ├── vehicle.py
│   │   ├── reminder.py
│   │   └── task_event.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── workers.py
│   │   ├── vehicles.py
│   │   ├── reminders.py
│   │   ├── metrics.py
│   │   └── chat.py
│   └── utils/
│       ├── ai_chat.py
│       ├── auth.py
│       ├── scheduler.py
│       └── twilio_client.py
├── frontend/
│   └── src/
│       ├── pages/          # Dashboard, Workers, Vehicles, Reminders, etc.
│       ├── components/     # Reusable UI components
│       ├── api/            # Axios API clients per resource
│       └── context/        # Auth context
├── docker-compose.yml
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- A [Twilio](https://www.twilio.com/) account (Account SID, Auth Token, WhatsApp/SMS number)
- An [OpenAI](https://platform.openai.com/) API key

### 1. Clone the repository

```bash
git clone https://github.com/decoder3064/Pulse.git
cd Pulse
```

### 2. Configure environment variables

Create a `.env` file inside the `backend/` directory:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/whatsapp_bot
REDIS_URL=redis://redis:6379/0

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

OPENAI_API_KEY=your_openai_api_key

JWT_SECRET_KEY=your_secret_key
```

### 3. Start the stack

```bash
docker compose up --build
```

This starts six services:

| Service | Description | Port |
|---|---|---|
| `db` | PostgreSQL 16 | 5433 |
| `redis` | Redis 7 | 6379 |
| `backend` | Flask API | 5001 |
| `celery-worker` | Processes reminder tasks | — |
| `celery-beat` | Schedules periodic tasks | — |
| `frontend` | React app (Nginx) | 80 |

### 4. Initialize the database

```bash
docker compose exec backend flask init-db
```

To seed mock data:

```bash
docker compose exec backend flask add-mock-data
```

### 5. Open the app

Visit [http://localhost](http://localhost) in your browser.

---

## API Overview

All routes are prefixed with `/api`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticate and receive a JWT |
| `GET` | `/api/workers` | List all workers |
| `POST` | `/api/workers` | Create a worker |
| `GET` | `/api/vehicles` | List all vehicles |
| `POST` | `/api/vehicles` | Add a vehicle |
| `GET` | `/api/reminders` | List all reminders |
| `POST` | `/api/reminders` | Schedule a new reminder |
| `GET` | `/api/metrics` | Dashboard summary data |
| `POST` | `/api/chat` | Send a message to the AI assistant |

A full Postman collection is available in the `postman/` directory.

---

## Running Locally (without Docker)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r ../requirements.txt
flask init-db
flask run --port 5001

# Celery (separate terminals)
celery -A tasks worker --loglevel=info
celery -A tasks beat --loglevel=info

# Frontend
cd frontend
npm install
npm run dev
```

Make sure PostgreSQL and Redis are running locally and your `.env` is configured accordingly.

---

## License

MIT
