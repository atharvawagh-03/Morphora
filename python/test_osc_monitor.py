"""Listen on OSC port 7000 and print incoming Morphora messages."""

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from config import OSC_IP, OSC_PORT


def _print(label: str):
    def handler(_addr, *args):
        print(f"{label}: {args[0] if len(args) == 1 else args}")

    return handler


def main() -> None:
    disp = Dispatcher()
    disp.map("/gesture/state", _print("STATE"))
    disp.map("/gesture/event", _print("EVENT"))
    disp.map("/gesture/left", _print("LEFT "))
    disp.map("/gesture/right", _print("RIGHT"))
    disp.map("/gesture/alive", lambda _a, *_: None)  # suppress heartbeat spam

    server = BlockingOSCUDPServer((OSC_IP, OSC_PORT), disp)
    print(f"Morphora OSC monitor on {OSC_IP}:{OSC_PORT}")
    print("Run python/main.py in another terminal. Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
