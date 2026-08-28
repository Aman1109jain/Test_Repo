from flask import Flask, request, render_template_string, redirect
import sqlite3
import os
import subprocess
import pickle

app = Flask(__name__)

# 1. Hardcoded secret key
app.secret_key = "super-secret-key-123"

# 2. Hardcoded database credentials / configuration
DB_USER = "admin"
DB_PASSWORD = "admin123"
DB_HOST = "localhost"


def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


# 3. SQL Injection
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        # VULNERABLE: user input directly concatenated into SQL
        query = (
            "SELECT * FROM users "
            "WHERE username = '" + username +
            "' AND password = '" + password + "'"
        )

        user = db.execute(query).fetchone()

        if user:
            return "Welcome " + username

        return "Invalid credentials"

    return """
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <button>Login</button>
        </form>
    """


# 4. Command Injection
@app.route("/ping")
def ping():
    host = request.args.get("host")

    # VULNERABLE: shell command contains user input
    result = subprocess.check_output(
        "ping -n 1 " + host,
        shell=True
    )

    return result.decode()


# 5. Path Traversal
@app.route("/read")
def read_file():
    filename = request.args.get("file")

    # VULNERABLE: user controls the file path
    with open(filename, "r") as f:
        return f.read()


# 6. Arbitrary file write
@app.route("/write", methods=["POST"])
def write_file():
    filename = request.form["file"]
    content = request.form["content"]

    # VULNERABLE: attacker controls filename
    with open(filename, "w") as f:
        f.write(content)

    return "File written"


# 7. Insecure deserialization
@app.route("/load", methods=["POST"])
def load_data():
    data = request.get_data()

    # VULNERABLE: pickle can execute arbitrary code
    obj = pickle.loads(data)

    return str(obj)


# 8. Weak password hashing
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    # VULNERABLE: MD5 is unsuitable for password storage
    password_hash = hashlib.md5(
        password.encode()
    ).hexdigest()

    db = get_db()

    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password_hash)
    )

    db.commit()

    return "Registered successfully"


# 9. Reflected XSS
@app.route("/search")
def search():
    query = request.args.get("q", "")

    # VULNERABLE: unescaped user input inserted into HTML
    html = """
    <html>
        <body>
            <h1>Search Results</h1>
            <p>You searched for: %s</p>
        </body>
    </html>
    """ % query

    return render_template_string(html)


# 10. Debug mode enabled
if __name__ == "__main__":
    # VULNERABLE: debug mode should not be enabled in production
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
