# CSCE_703_Project_3_OWASP_Juice_Shop

Christian Kane's CSCE 703 Project 3: OWASP Juice Shop.

This repository explores web application security using [OWASP Juice Shop](https://owasp-juice.shop/), a deliberately vulnerable web app, and applies the resulting lessons to a small login form built from scratch.

## Part 1 — Secure Feature Design

Vulnerabilities were identified and exploited hands-on against a local Juice Shop instance:

1. **SQL Injection (authentication bypass)** — logging in with email `' OR 1=1--` returns a valid session for the admin account without knowing the password, because the login query is built from unparameterized string concatenation.
2. **DOM-based XSS** — the search bar renders the query string into the page via an unsanitized `innerHTML` binding, so `<iframe src="javascript:alert('xss')">` executes as script.
3. **Mass assignment / broken access control** — the raw REST registration endpoint (`/api/Users/`) accepts a client-supplied `role` field, letting anyone self-register as `"role": "admin"`.

**Mitigations:** parameterized queries/ORM bindings (never concatenate user input into SQL); output encoding plus a strict Content-Security-Policy for XSS; and a server-side field allow-list on registration that ignores any client-supplied `role`. Passwords should be hashed with a slow, salted algorithm such as bcrypt (e.g. `bcrypt.hash(password, 12)`), never stored in plaintext or a fast hash like MD5.

## Part 2 — Login Form

[`login-form/`](login-form/) contains a small login form built to apply the Part 1 lessons directly, with both client-side and server-side validation.

### Structure

```
login-form/
├── public/
│   ├── index.html   # login form markup
│   ├── style.css     # Juice-Shop-inspired dark/orange styling
│   └── script.js      # client-side validation + fetch call to the API
└── server.py          # Python stdlib backend (http.server + sqlite3 + hashlib)
```

### What it does

- **Client-side validation** (`script.js`): blocks submission if either field is empty, the email doesn't contain `@`, or the password is under 8 characters — giving immediate feedback before any network call.
- **Server-side validation** (`server.py`): re-checks the same rules server-side (the client can always be bypassed), since server-side is the only validation that can actually be trusted.
- **Secure storage**: passwords are hashed with `hashlib.pbkdf2_hmac` (SHA-256, 100,000 iterations) and a random per-user salt — no plaintext passwords are ever stored.
- **SQL Injection resistant**: the login lookup uses a parameterized query (`WHERE email = ?`), so injected SQL is treated as a literal string value, never as executable SQL.
- **XSS resistant**: the server never echoes raw user input back in a response, and the client writes all messages via `textContent` (never `innerHTML`), so injected markup/script cannot execute.
- **Generic auth errors**: invalid email and invalid password both return the same "Invalid email or password" message, to avoid leaking which accounts exist (user enumeration).

### Running it

Requires only Python 3 (standard library, no `pip install` needed):

```powershell
python login-form/server.py
```

Then open [http://localhost:8080](http://localhost:8080). A seeded test account is available:

- Email: `test@juice-shop-form.com`
- Password: `SecurePass123`

## Part 3 — Exploiting the Login Form

See the project write-up for the attempted SQL Injection and XSS attacks against the form above, why they failed, and the security lessons learned.

## Running Juice Shop locally (for Part 1 exploration)

```powershell
docker pull bkimminich/juice-shop
docker run -d -p 3000:3000 --name juice-shop bkimminich/juice-shop
```

Then open [http://localhost:3000](http://localhost:3000).
