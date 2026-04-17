import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------ DATABASE SETUP ------------------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()

    if user:
        session['user_id'] = user[0]
        return redirect('/dashboard')
    else:
        # if not exist → create user automatically
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        session['user_id'] = c.lastrowid
        return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM tasks WHERE user_id=?", (session['user_id'],))
    tasks = c.fetchall()

    conn.close()

    return render_template('dashboard.html', tasks=tasks)


@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form['task']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (session['user_id'], task))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


@app.route('/delete_task/<int:id>')
def delete_task(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)