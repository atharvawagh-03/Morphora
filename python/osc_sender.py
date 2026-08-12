"""OSC sender — pushes gesture state and events to TouchDesigner."""

from pythonosc.udp_client import SimpleUDPClient

from config import (
    OSC_ADDR_ALIVE,
    OSC_ADDR_EVENT,
    OSC_ADDR_LEFT,
    OSC_ADDR_RIGHT,
    OSC_ADDR_STATE,
    OSC_IP,
    OSC_PORT,
    SystemState,
)


class OSCSender:
    def __init__(self, ip: str = OSC_IP, port: int = OSC_PORT) -> None:
        self._client = SimpleUDPClient(ip, port)
        self._last_state: SystemState | None = None

    def send_state(self, state: SystemState) -> None:
        if state != self._last_state:
            self._client.send_message(OSC_ADDR_STATE, int(state))
            self._last_state = state

    def send_event(self, event: str) -> None:
        self._client.send_message(OSC_ADDR_EVENT, event)

    def send_hands(self, left: str, right: str) -> None:
        self._client.send_message(OSC_ADDR_LEFT, left)
        self._client.send_message(OSC_ADDR_RIGHT, right)

    def send_alive(self) -> None:
        self._client.send_message(OSC_ADDR_ALIVE, 1)
