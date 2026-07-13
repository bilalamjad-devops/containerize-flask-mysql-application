import os
from contextlib import contextmanager

from flask import Flask, render_template, request
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DEBUG_MODE = os.getenv("FLASK_DEBUG", "false").lower() == "true"

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "web_db")

if not DB_NAME.replace("_", "").isalnum():
    raise ValueError(f"Invalid DB_NAME: {DB_NAME!r}")


@contextmanager
def get_db_cursor():
    """Yields (connection, cursor) and guarantees cleanup on error."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content VARCHAR(255)
            )
            """
        )
        conn.commit()
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    data = request.form.get("user_data", "").strip()

    if not data:
        return render_template("index.html", message="\u274c No input provided.")

    try:
        with get_db_cursor() as (conn, cursor):
            cursor.execute("INSERT INTO users (content) VALUES (%s)", (data,))
            conn.commit()
        message = f"\U0001f389 Saved '{data}' to the database."
    except Exception as e:
        app.logger.error("Database write failed: %s", e)
        message = "\u274c Could not save your data. Please try again."

    return render_template("index.html", message=message)


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=DEBUG_MODE)
