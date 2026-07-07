# CSCE_703_Project_3_OWASP_Juice_Shop

Christian Kane's CSCE 703 Project 3: OWASP Juice Shop.

[`login-form/`](login-form/) contains a login form styled after Juice Shop's own login page, with both client-side and server-side validation.

## Structure

```
login-form/
├── public/
│   ├── index.html   # login form markup
│   ├── style.css     # Juice-Shop-inspired dark/orange styling
│   └── script.js      # client-side validation + fetch call to the API
└── server.py          # Python stdlib backend (http.server + sqlite3 + hashlib)
```

## What it does

- **Client-side validation** (`script.js`): blocks submission if either field is empty, the email doesn't contain `@`, or the password is under 8 characters — giving immediate feedback before any network call.
- **Server-side validation** (`server.py`): re-checks the same rules server-side (the client can always be bypassed), since server-side is the only validation that can actually be trusted.
- **Secure storage**: passwords are hashed with `hashlib.pbkdf2_hmac` (SHA-256, 100,000 iterations) and a random per-user salt — no plaintext passwords are ever stored.
- **SQL Injection resistant**: the login lookup uses a parameterized query (`WHERE email = ?`), so injected SQL is treated as a literal string value, never as executable SQL.
- **XSS resistant**: the server never echoes raw user input back in a response, and the client writes all messages via `textContent` (never `innerHTML`), so injected markup/script cannot execute.
- **Generic auth errors**: invalid email and invalid password both return the same "Invalid email or password" message, to avoid leaking which accounts exist (user enumeration).

## Running it

Requires only Python 3 (standard library, no `pip install` needed):

```powershell
python login-form/server.py
```

Then open [http://localhost:8080](http://localhost:8080). A seeded test account is available:

- Email: `test@juice-shop-form.com`
- Password: `SecurePass123`
