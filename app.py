import os, io, base64, re
import pandas as pd
import matplotlib.pyplot as plt
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import get_db_connection, init_db

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__, instance_relative_config=True)
app.config["SECRET_KEY"] = "super-secret-key-change-in-prod"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

init_db()

# ---------- HELPERS ----------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    return get_db_connection()

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def save_plot(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return img_base64

# ---------- ROUTES ----------
@app.route("/")
def index():
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("admin_dashboard"))
    if role == "user":
        return redirect(url_for("user_dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        address = request.form["address"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not all([name, email, password, confirm_password]):
            flash("All fields are required.", "warning")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if not validate_password(password):
            flash("Password must be at least 8 chars, include uppercase, number, and special char.", "danger")
            return redirect(url_for("register"))

        role = "admin" if email.endswith("@quantumsoft.net") else "user"
        conn = get_db()
        try:
            hashed_pw = generate_password_hash(password)
            conn.execute(
                "INSERT INTO users (name, email, address, password, role) VALUES (?, ?, ?, ?, ?)",
                (name, email, address, hashed_pw, role)
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Registration failed: {e}", "danger")
        finally:
            conn.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            flash("Welcome back!", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

@app.route("/user/dashboard")
def user_dashboard():
    if session.get("role") not in ("user", "admin"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    return render_template("user_dashboard.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Admins only.", "danger")
        return redirect(url_for("index"))
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".csv")]
    return render_template("admin_dashboard.html", files=files)

@app.route("/admin/users")
def admin_users():
    if session.get("role") != "admin":
        flash("Admins only.", "danger")
        return redirect(url_for("index"))
    conn = get_db()
    users = conn.execute("SELECT id, name, email, role, address FROM users").fetchall()
    conn.close()
    return render_template("admin_users.html", users=users)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file selected.", "warning")
        return redirect(url_for("user_dashboard"))
    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("user_dashboard"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        return redirect(url_for("analyze", filename=filename))
    else:
        flash("Invalid file type. Please upload a CSV.", "danger")
        return redirect(url_for("user_dashboard"))

@app.route("/analyze/<path:filename>")
def analyze(filename):
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(path):
        flash("File not found.", "danger")
        return redirect(url_for("user_dashboard"))
    df = pd.read_csv(path)
    shape = df.shape
    dtypes = df.dtypes.apply(lambda x: x.name).to_dict()
    describe_html = df.describe(include='all').to_html(classes="table table-sm table-striped", border=0)
    missing_html = (df.isnull().sum() / len(df) * 100).round(2).to_frame("Missing %").to_html(classes="table table-sm table-striped", border=0)
    plot_images = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) > 0:
        fig = plt.figure()
        df[numeric_cols[0]].dropna().hist(bins=20, color="#5a43f1")
        plt.title(f"Histogram: {numeric_cols[0]}")
        plot_images.append(save_plot(fig))
    if len(numeric_cols) >= 2:
        fig = plt.figure()
        df.plot.scatter(x=numeric_cols[0], y=numeric_cols[1], color="#7a5fff")
        plt.title(f"Scatter: {numeric_cols[0]} vs {numeric_cols[1]}")
        plot_images.append(save_plot(fig))
    return render_template(
        "analyze.html",
        filename=filename,
        shape=shape,
        dtypes=dtypes,
        describe_html=describe_html,
        missing_html=missing_html,
        plot_images=plot_images
    )

@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
