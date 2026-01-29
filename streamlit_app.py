import streamlit as st
import requests
import websocket
import json
import threading
import queue
import time

API_BASE = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/chat/ws?room=general"


# -----------------------------
# Session state (SAFE)
# -----------------------------
if "jwt" not in st.session_state:
    st.session_state.jwt = None

if "ws" not in st.session_state:
    st.session_state.ws = None

if "connected" not in st.session_state:
    st.session_state.connected = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ws_queue" not in st.session_state:
    st.session_state.ws_queue = queue.Queue()


# -----------------------------
# WebSocket listener (NO Streamlit calls)
# -----------------------------
def listen_ws(ws, q):
    while True:
        try:
            msg = ws.recv()
            q.put(json.loads(msg))
        except Exception:
            break


# -----------------------------
# UI
# -----------------------------
st.title("💬 Chat App")

with st.sidebar:
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(
            f"{API_BASE}/auth/login",
            params={
                "username": username,
                "password": password,
            },
        )

        if res.status_code == 200:
            st.session_state.jwt = res.json()["access_token"]
            st.success("Logged in")
        else:
            st.error(res.text)

    st.divider()

    if st.button("Connect WebSocket"):
        if not st.session_state.jwt:
            st.error("Login first")
        else:
            ws = websocket.WebSocket()
            ws.connect(
                WS_URL,
                header=[f"Authorization: Bearer {st.session_state.jwt}"],
            )

            st.session_state.ws = ws
            st.session_state.connected = True

            threading.Thread(
                target=listen_ws,
                args=(ws, st.session_state.ws_queue),
                daemon=True,
            ).start()

            st.success("Connected")


# -----------------------------
# Pull WS messages safely
# -----------------------------
while not st.session_state.ws_queue.empty():
    data = st.session_state.ws_queue.get()
    st.session_state.messages.append(
        f"{data.get('sender')}: {data.get('content')}"
    )


# -----------------------------
# Chat display (NO fixed height)
# -----------------------------
for msg in st.session_state.messages:
    st.write(msg)


# -----------------------------
# Send message
# -----------------------------
msg = st.text_input("Message")

if st.button("Send"):
    if not st.session_state.connected:
        st.error("Not connected")
    else:
        st.session_state.ws.send(
            json.dumps({"content": msg})
        )
        st.session_state.messages.append(f"You: {msg}")
        st.rerun()
