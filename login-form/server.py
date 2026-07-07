import hashlib
import http.server
import json
import secrets
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"
PUBLIC_DIR = BASE_DIR / "public"
PORT = 8080

TEST_EMAIL = "test@juice-shop-form.com"
TEST_PASSWORD = "SecurePass123"


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY, "
        "email TEXT UNIQUE NOT NULL, "
        "salt TEXT NOT NULL, "
        "password_hash TEXT NOT NULL)"
    )
    existing = conn.execute("SELECT 1 FROM users WHERE email = ?", (TEST_EMAIL,)).fetchone()
    if not existing:
        salt = secrets.token_hex(16)
        conn.execute(
            "INSERT INTO users (email, salt, password_hash) VALUES (?, ?, ?)",
            (TEST_EMAIL, salt, hash_password(TEST_PASSWORD, salt)),
        )
    conn.commit()
    conn.close()


def validate_credentials(email, password):
    if not email or not password:
        return "Email and password are required."
    if "@" not in email:
        return "Please enter a valid email address."
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    return None


class LoginHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_POST(self):
        if self.path != "/api/login":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"success": False, "message": "Malformed request."})
            return

        email = str(payload.get("email", "")).strip()
        password = str(payload.get("password", ""))

        validation_error = validate_credentials(email, password)
        if validation_error:
            self._send_json(400, {"success": False, "message": validation_error})
            return

        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT salt, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if row and secrets.compare_digest(hash_password(password, row[0]), row[1]):
            self._send_json(200, {"success": True, "message": "Login successful."})
        else:
            self._send_json(401, {"success": False, "message": "Invalid email or password."})

    def _send_json(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), LoginHandler)
    print(f"Serving login form on http://localhost:{PORT}")
    server.serve_forever()
