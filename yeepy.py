# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import sqlite3, random
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

DATABASE = 'quiz_data.db'
app = Flask(__name__)
app.secret_key = 'change_this_to_a_random_secret'  # <-- เปลี่ยนก่อน deploy

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated

# Home / Dashboard (public)
@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            return render_template('register.html', error="กรุณากรอกข้อมูลให้ครบ")
        db = get_db()
        try:
            pw_hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                       (username, pw_hash, datetime.utcnow().isoformat()))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="ชื่อผู้ใช้ซ้ำ ลองชื่ออื่น")
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# User dashboard (after login)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

# Tool page (converter)
@app.route('/tool')
@login_required
def tool():
    return render_template('tool.html')

# Quiz page (UI)
@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')

# API: random question (JSON)
@app.route('/api/random_question')
@login_required
def random_question():
    db = get_db()
    cur = db.execute("SELECT id, question, choice1, choice2, choice3 FROM questions")
    rows = cur.fetchall()
    if not rows:
        return jsonify({'error': 'no questions'}), 404
    q = random.choice(rows)
    return jsonify({
        'id': q['id'],
        'question': q['question'],
        'choices': [q['choice1'], q['choice2'], q['choice3']]
    })

# API: submit answer -> save score
@app.route('/api/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    data = request.get_json()
    qid = data.get('question_id')
    selected = data.get('selected')
    db = get_db()
    cur = db.execute("SELECT answer FROM questions WHERE id = ?", (qid,))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'invalid question'}), 400
    correct = (selected == row['answer'])
    # save score entry: score=1 if correct else 0, total=1
    db.execute("INSERT INTO scores (user_id, score, total, created_at) VALUES (?, ?, ?, ?)",
               (session['user_id'], 1 if correct else 0, 1, datetime.utcnow().isoformat()))
    db.commit()
    return jsonify({'correct': correct, 'correct_answer': row['answer']})

# View user's past scores
@app.route('/scores')
@login_required
def scores():
    db = get_db()
    cur = db.execute("SELECT score, total, created_at FROM scores WHERE user_id = ? ORDER BY created_at DESC", (session['user_id'],))
    rows = cur.fetchall()
    return render_template('scores.html', rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
