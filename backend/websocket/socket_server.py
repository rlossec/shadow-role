import socketio
from core.config import settings

sio_server = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)


sio_app = socketio.ASGIApp(
    socketio_server=sio_server,
    socketio_path=settings.SOCKETIO_PATH,
)


@sio_server.event
async def connect(sid, environ, auth):
    print(f"{sid} connected")


@sio_server.event
async def disconnect(sid):
    print(f'{sid}: disconnected')


__all__ = ["sio_server", "sio_app"]