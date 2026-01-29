# Real-Time Chat Application

A learning-focused real-time chat application built with FastAPI, WebSockets, JWT authentication, PostgreSQL, and Streamlit.

## Tech Stack
- FastAPI (Backend & REST APIs)
- WebSockets (Real-time messaging)
- JWT Authentication
- PostgreSQL (Persistent storage)
- Streamlit (Frontend UI)

## Features
- User authentication (signup/login) with JWT
- Authenticated WebSocket connections
- Real-time message broadcasting
- Message persistence in PostgreSQL
- Room-based chat support
- Minimal Streamlit frontend

## Architecture Overview
1. User logs in via REST API
2. JWT is issued and stored client-side
3. WebSocket connection established using JWT header
4. Messages are broadcast and stored in database

## Running the Project

### Backend
## Run Locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend
```bash
streamlit run app.py