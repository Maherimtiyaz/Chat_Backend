# Real-Time Chat Backend (FastAPI)

A beginner-friendly real-time chat backend built using FastAPI and WebSockets.

## Features
- JWT Authentication
- Password hashing (bcrypt)
- WebSocket-based real-time chat
- Clean project structure

## Tech Stack
- Python
- FastAPI
- WebSockets
- JWT
- bcrypt

## Run Locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
