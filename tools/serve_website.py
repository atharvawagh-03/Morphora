#!/usr/bin/env python3
"""
Simple HTTP preview server for the Morphora showcase website.

Usage:
    python tools/serve_website.py
    python tools/serve_website.py --port 8080
"""

import argparse
import http.server
import os
import socketserver
import webbrowser
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Serve Morphora showcase website locally.")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    args = parser.parse_args()

    website_dir = Path(__file__).resolve().parent.parent / "website"
    if not website_dir.exists():
        raise FileNotFoundError(f"Website directory not found at {website_dir}")

    os.chdir(website_dir)

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            super().end_headers()

    with socketserver.TCPServer(("", args.port), CustomHandler) as httpd:
        url = f"http://localhost:{args.port}"
        print(f"=================================================")
        print(f"  Morphora Showcase Website running at:")
        print(f"  {url}")
        print(f"  Serving files from: {website_dir}")
        print(f"  Press Ctrl+C to stop the server")
        print(f"=================================================")

        if not args.no_browser:
            webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
