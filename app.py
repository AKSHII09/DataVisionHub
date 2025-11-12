from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, add_user, get_user_by_email, get_all_users
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

init_db()

# ---------- Home ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- Register ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        address = request.form['address']

        if password != confirm:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c in "!@#$%^&*" for c in password):
            flash("Password must be strong (8 chars, 1 uppercase, 1 special)", "danger")
            return redirect(url_for('register'))

        role = "admin" if email.endswith("@quantumsoft.net") else "user"
        add_user(name, email, password, address, role)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------- Login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)

        if user and user[3] == password:
            session['name'] = user[1]
            session['role'] = user[5]
            if user[5] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('index'))

# ---------- User Dashboard ----------
@app.route('/user/dashboard')
def user_dashboard():
    if 'name' not in session:
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

# ---------- Admin Dashboard ----------
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'name' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    users = get_all_users()
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('admin_dashboard.html', users=users, files=files)

# ---------- Upload & Analyze ----------
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            df = pd.read_csv(filepath)
            plt.figure(figsize=(8, 5))
            df.plot(kind='bar')
            plt.title('Data Visualization')
            plt.tight_layout()
            plot_path = os.path.join('static', 'images', 'plot.png')
            plt.savefig(plot_path)
            plt.close()

            return render_template('analyze.html', columns=list(df.columns), plot=plot_path)
        else:
            flash("Please upload a valid CSV file.", "danger")
            return redirect(url_for('analyze'))

    return render_template('analyze.html')

if __name__ == '__main__':
    app.run(debug=True)
