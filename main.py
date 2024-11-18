import http.server
import socketserver
import os
import gzip
from io import BytesIO

PORT = 8080

class MyHttpRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        # Extract headers to determine if gzip is accepted
        accept_encoding = self.headers.get('Accept-Encoding', '')

        # Get the requested path
        path = self.path.strip('/')

        # Handle file requests
        if path.startswith("file/"):
            file_path = path[len("file/"):]
            if os.path.exists(file_path):  # Check if the file exists
                with open(file_path, "rb") as file:
                    file_data = file.read()

                # Check if client accepts gzip
                if "gzip" in accept_encoding:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Encoding", "gzip")
                    self.end_headers()

                    # Compress response
                    gzip_data = gzip.compress(file_data)
                    self.wfile.write(gzip_data)
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.end_headers()
                    self.wfile.write(file_data)
            else:
                # File not found response
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write("File not found!".encode('utf-8'))
        
        else:
            # Default response for other paths
            if path == "":
                response_body = "Hello! You requested: /".encode('utf-8')
            else:
                response_body = f"You requested: {path}".encode('utf-8')

            # Check if client accepts gzip
            if "gzip" in accept_encoding:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Encoding", "gzip")
                self.end_headers()

                # Compress response
                gzip_data = gzip.compress(response_body)
                self.wfile.write(gzip_data)
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(response_body)

    # Handle POST requests
    def do_POST(self):
        # Read the request body
        content_length = int(self.headers.get("Content-Length", 0))
        request_body = self.rfile.read(content_length).decode("utf-8")
        print(f"Received POST request with body: {request_body}")

        # Respond with request body
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_compression_headers()
        self.end_headers()
        self.wfile.write(f"Received POST data: {request_body}".encode("utf-8"))

    # Add compression headers
    def send_compression_headers(self):
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Vary", "Accept-Encoding")

    # Compress data with gzip
    @staticmethod
    def compress_with_gzip(data):
        compressed_buffer = BytesIO()
        with gzip.GzipFile(fileobj=compressed_buffer, mode="wb") as gzip_file:
            gzip_file.write(data)
        return compressed_buffer.getvalue()


# Enable concurrency using ThreadingMixIn
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), MyHttpRequestHandler)
    print(f"Serving on port {PORT}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server.")
        server.server_close()
