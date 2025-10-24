from flask import Flask, request, session, jsonify, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os

app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))

# Dummy user store
USER = {
    "username": "admin",
    "password_hash": generate_password_hash("password123")
}

@app.route("/", methods=["GET"])
def index():
    logged_in = session.get("user") == USER["username"]
    username = session.get("user") if logged_in else ""
    
    template = """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <title>Dummy Login - Vercel</title>
      <style>
        body { font-family: Arial, sans-serif; background:#f7f7f7; padding:40px; }
        .card { background:white; border-radius:6px; padding:20px; max-width:420px; margin:0 auto; box-shadow:0 2px 6px rgba(0,0,0,0.08); }
        input[type=text], input[type=password] { width:100%; padding:8px; margin:6px 0 12px 0; box-sizing:border-box; }
        button { padding:8px 14px; border:none; background:#2b7cff; color:white; border-radius:4px; cursor:pointer; }
        .msg { margin:10px 0; color:#b00; }
        .success { color: #0a7; }
      </style>
    </head>
    <body>
      <div class="card" id="app">
        <h2>Dummy Login (Vercel)</h2>
        <div id="login-panel" style="display: {{ 'none' if logged_in else 'block' }};">
          <label>Username</label>
          <input id="username" type="text" value="admin" />
          <label>Password</label>
          <input id="password" type="password" />
          <div>
            <button id="login-btn">Log in</button>
          </div>
          <div class="msg" id="error-msg" aria-live="polite"></div>
        </div>
        <div id="welcome-panel" style="display: {{ 'block' if logged_in else 'none' }};">
          <p id="welcome-text">Welcome, <strong>{{ username }}</strong>!</p>
          <p>You are logged in to the Vercel-deployed dummy app.</p>
          <div>
            <button id="logout-btn">Log out</button>
          </div>
          <div class="msg success" id="ok-msg" aria-live="polite"></div>
        </div>
      </div>
      <script>
      document.addEventListener('DOMContentLoaded', function() {
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const err = document.getElementById('error-msg');
        const ok = document.getElementById('ok-msg');

        if (loginBtn) {
          loginBtn.addEventListener('click', async () => {
            err.textContent = '';
            ok.textContent = '';
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
              const res = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
              });
              const data = await res.json();
              if (res.ok) {
                document.getElementById('login-panel').style.display = 'none';
                document.getElementById('welcome-panel').style.display = 'block';
                document.getElementById('welcome-text').innerHTML = 'Welcome, <strong>' + data.username + '</strong>!';
                ok.textContent = 'Login successful.';
              } else {
                err.textContent = data.error || 'Login failed.';
              }
            } catch (e) {
              err.textContent = 'Network error.';
            }
          });
        }

        if (logoutBtn) {
          logoutBtn.addEventListener('click', async () => {
            err.textContent = '';
            ok.textContent = '';
            try {
              const res = await fetch('/logout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
              });
              if (res.ok) {
                document.getElementById('login-panel').style.display = 'block';
                document.getElementById('welcome-panel').style.display = 'none';
                ok.textContent = 'Logged out.';
                document.getElementById('password').value = '';
              } else {
                const data = await res.json();
                err.textContent = data.error || 'Logout failed.';
              }
            } catch (e) {
              err.textContent = 'Network error.';
            }
          });
        }
      });
      </script>
    </body>
    </html>
    """
    return render_template_string(template, logged_in=logged_in, username=username)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body, JSON expected."}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if username != USER["username"]:
        return jsonify({"error": "Invalid credentials."}), 401

    if not check_password_hash(USER["password_hash"], password):
        return jsonify({"error": "Invalid credentials."}), 401

    session["user"] = username
    return jsonify({"message": "Logged in", "username": username}), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out"}), 200

if __name__ == "__main__":
    app.run(debug=True)