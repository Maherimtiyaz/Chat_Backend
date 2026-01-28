import streamlit as st
import websocket
import threading
import json
import time

st.set_page_config(page_title="Chat Client", layout="centered")
st.title("💬 Real-Time Chat")

# ----------------------------
# Session state initialization
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "ws" not in st.session_state:
    st.session_state.ws = None

if "connected" not in st.session_state:
    st.session_state.connected = False

if "error" not in st.session_state:
    st.session_state.error = None


# ----------------------------
# WebSocket helpers
# ----------------------------
def ws_is_open(ws):
    try:
        return ws and ws.sock and ws.sock.connected
    except Exception:
        return False


def on_message(ws, message):
    """
    Callback when a message is received from the server.
    Messages are appended to session_state and UI will show them on next rerun.
    """
    try:
        data = json.loads(message)
        room = data.get("room", "unknown")
        sender = data.get("sender", "unknown")
        msg = data.get("message", "")
        st.session_state.messages.append(f"{sender} [{room}]: {msg}")
    except Exception as e:
        st.session_state.messages.append(f"Malformed message: {message}")
    st.experimental_rerun()


def on_error(ws, error):
    st.session_state.error = f"WebSocket error: {error}"
    st.session_state.connected = False
    st.experimental_rerun()


def on_close(ws, close_status_code, close_msg):
    st.session_state.connected = False
    st.session_state.messages.append("🔴 Disconnected from server")
    st.experimental_rerun()


def connect_ws(token, room):
    """
    Connect to WebSocket with JWT token and room name.
    """
    headers = [f"Authorization: Bearer {token}"]
    ws = websocket.WebSocketApp(
        f"ws://127.0.0.1:8000/chat/ws?room={room}",
        header=headers,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    thread = threading.Thread(target=ws.run_forever, daemon=True)
    thread.start()
    return ws


# ----------------------------
# UI Elements
# ----------------------------
token = st.text_input("JWT Token", type="password")
room = st.text_input("Room", value="general")

# Connect button
if st.button("Connect"):
    if token.strip():
        st.session_state.ws = connect_ws(token.strip(), room.strip())
        st.session_state.connected = True
        st.session_state.messages.append(f"🟢 Connected to room '{room.strip()}'")
    else:
        st.warning("Please provide a JWT token")

st.divider()

# Input for sending message
message = st.text_input("Message")

if st.button("Send"):
    ws = st.session_state.get("ws")
    if not st.session_state.connected or not ws_is_open(ws):
        st.error("WebSocket is not connected. Please reconnect.")
    elif message.strip():
        try:
            # Send message to backend
            ws.send(message.strip())
            # Optimistic UI update
            st.session_state.messages.append(f"You [{room.strip()}]: {message.strip()}")
        except Exception as e:
            st.error(f"Failed to send message: {e}")

st.divider()

# Display chat messages
st.subheader("Chat Messages")
for msg in st.session_state.messages:
    st.write(msg)

# Show errors if any
if st.session_state.error:
    st.error(st.session_state.error)
