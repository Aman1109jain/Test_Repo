### Vulnerable Python Program — For Security Practice

```python
from flask import Flask, request
import sqlite3
import subprocess
import os

app = Flask(__name__)

# 1. Hardcoded credentials
USERNAME = "admin"
PASSWORD = "admin123"


# 2. SQL Injection vulnerability
@app.route("/user")
def get_user():
    username = request.args.get("username")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Vulnerable: user input is directly inserted into SQL
    query = "SELECT * FROM users WHERE username = '" + username + "'"

    cursor.execute(query)
    user = cursor.fetchone()

    conn.close()

    return str(user)


# 3. Command Injection vulnerability
@app.route("/ping")
def ping():
    host = request.args.get("host")

    # Vulnerable: untrusted input is passed to a shell
    result = subprocess.check_output(
        "ping -c 1 " + host,
        shell=True
    )

    return result.decode()


# 4. Debug mode enabled
@app.route("/")
def home():
    return "Welcome to Vulnerable Application!"


if __name__ == "__main__":
    # Vulnerable configuration for demonstration
    app.run(debug=True, host="0.0.0.0")

