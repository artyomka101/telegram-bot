#!/usr/bin/env python3
"""
Main entry point for the Telegram bot application.
This file serves as the primary entry point for deployment platforms.
"""

import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()


def start_health_server():
    """Start a simple HTTP server for health checks"""
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()


def main():
    """Main function to start the bot"""
    # Start health check server in a separate thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Import and run the bot
    try:
        from bot.main import main as bot_main
        bot_main()
    except ImportError as e:
        print(f"Error importing bot module: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
