from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client
import os



load_dotenv()

client = OpenAI()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

HOST = "127.0.0.1"
PORT = 8000



def embed_query(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding



def semantic_search(query_text: str) -> list[dict]:
    emb_q = embed_query(query_text)

    res = sb.rpc(
        "match_chunks",
        {
            "query_embedding": emb_q,
            "match_count": 5
        }
    ).execute()

    rows = res.data or []
    print("RAG OUTPUT:", rows)
    return rows


class SimpleHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(
            b"Server is running. Use POST /chat with JSON {'prompt':'...'}"
        )

    def do_POST(self):
        if self.path != "/chat":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        prompt = data.get("prompt", "").strip()

        # 🔍 Retrieve context ONCE
        matches = semantic_search(prompt)
        context = "\n\n".join(m.get("content", "") for m in matches)

        # 🧠 System prompt with RAG
        system_prompt = (
            "You are a helpful and energetic assistant, "
            "a fitness trainer, gym and martial arts expert.\n\n"
            "Answer politely and accurately."
        )

        if context:
            system_prompt += (
                "\n\nUse the following retrieved context if relevant:\n"
                f"{context}"
            )

        # 🤖 LLM call
        response = client.responses.create(
            model="gpt-5-nano",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        reply_text = response.output_text

        self._set_headers()
        self.wfile.write(
            json.dumps({"reply": reply_text}).encode("utf-8")
        )


# -------------------- Run Server --------------------
if __name__ == "__main__":
    print(f"Server running at http://{HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), SimpleHandler)
    server.serve_forever()
