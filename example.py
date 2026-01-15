from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

HOST = "127.0.0.1"
PORT = 8000

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Server is running. Use POST /chat with JSON {'prompt':'...'}")

    def do_POST(self):
        if self.path == "/chat":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            prompt = data.get("prompt", "")

            response = client.responses.create(
                model="gpt-5-nano",
                input=[
    {"role": "system", "content": "You are a helpful and energetic assistant, a fitness trainer, gym and martial arts expert."},
    {"role": "user", "content": "How can I improve my boxing technique?"},
    {"role": "assistant", "content": "Focus on footwork, shadow boxing, and speed drills. Practice regularly and maintain proper stance."},
    {"role": "user", "content": prompt}
]

            )

            self._set_headers()
            reply = {"reply": response.output_text}
            self.wfile.write(json.dumps(reply).encode("utf-8"))

if __name__ == "__main__":
    print(f"Server running at http://{HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), SimpleHandler)
    server.serve_forever()