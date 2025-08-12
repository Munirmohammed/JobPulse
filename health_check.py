#!/usr/bin/env python3
"""
Simple health check server for deployment monitoring
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
from datetime import datetime

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                'status': 'healthy',
                'service': 'JobPulse',
                'timestamp': datetime.now().isoformat(),
                'message': 'JobPulse automation is running'
            }
            
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server(port=8080):
    """Start health check server in background"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"🏥 Health check server running on port {port}")
    return server

if __name__ == "__main__":
    start_health_server()
    print("Health check server started")
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Health check server stopped")
