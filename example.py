from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client
import os

# Load environment variables from .env file (API keys, URLs, etc.)
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Load Supabase credentials from environment
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Create Supabase client for database + RPC calls
sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Server settings
HOST = "127.0.0.1"
PORT = 8000

# Create embedding vector for a given text query

def embed_query(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    # Return 1536-dimension embedding vector
    return response.data[0].embedding


# Perform semantic search using Supabase RPC function
# match_chunks(query_embedding, match_count)

def semantic_search(query_text: str) -> list[dict]:
    # Step 1: embed the question
    emb_q = embed_query(query_text)

    # Step 2: call Supabase RPC function for vector similarity search
    res = sb.rpc(
        "match_chunks",
        {
            "query_embedding": emb_q,
            "match_count": 5
        }
    ).execute()

    # Extract rows (or empty list if nothing)
    rows = res.data or []
    print("RAG OUTPUT:", rows)
    return rows

# -----------------------------------------------------
# HTTP server handler (GET, POST, OPTIONS)
# -----------------------------------------------------
class SimpleHandler(BaseHTTPRequestHandler):

    # Convenience function to set default JSON headers
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    # Handle browser CORS preflight requests
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # Basic GET endpoint (health check)
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(
            b"Server is running. Use POST /chat with JSON {'prompt':'...'}"
        )

    # Main chatbot endpoint
    def do_POST(self):
        if self.path != "/chat":
            self.send_response(404)
            self.end_headers()
            return

        # Read JSON request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        # Extract user prompt
        prompt = data.get("prompt", "").strip()

        # Run semantic search (RAG retrieval)
        matches = semantic_search(prompt)

        # Combine retrieved context into a single text block
        context = "\n\n".join(m.get("content", "") for m in matches)

        # Build system prompt for the AI
        system_prompt = (
            "You are a helpful and energetic assistant, "
            "a fitness trainer, gym and martial arts expert.\n\n"
            "Answer politely and accurately."
        )

        # Add context if RAG found anything
        if context:
            system_prompt += (
                "\n\nUse the following retrieved context if relevant:\n"
                f"{context}"
            )

        # Send combined system + user prompt to OpenAI
        response = client.responses.create(
            model="gpt-5-nano",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
        )

        # Extract the model’s text output
        reply_text = response.output_text

        # Return JSON response
        self._set_headers()
        self.wfile.write(
            json.dumps({"reply": reply_text}).encode("utf-8")
        )

# Start HTTP server

if __name__ == "__main__":
    print(f"Server running at http://{HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), SimpleHandler)
    server.serve_forever()
