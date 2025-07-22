from flask import Flask, render_template, request, redirect, abort, flash, g, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import functools

DATABASE = 'greivances.db'

app = Flask(__name__)

app.secret_key="toastytoastytoast"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_greivance(id):
    conn = get_db_connection()
    greivance = conn.execute('SELECT * FROM greivances WHERE id = ?', (id,)).fetchone()
    conn.close()
    if greivance is None:
        abort(404)
    return greivance

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return render_template('login.html')
        return view(**kwargs)
    return wrapped_view

@app.route("/")
def display_form():
    return render_template('index.html')
@app.route('/submit', methods=('POST', 'GET'))
def submit_post():
    name = request.form['discordName']
    greivance = request.form['greivance']
    conn = get_db_connection()
    conn.execute('INSERT INTO greivances (name, greivance) values (?, ?)', (name, greivance))
    conn.commit()
    conn.close()
    return render_template('submitted.html')
@app.route('/view/')
@login_required
def get_list():
    conn = get_db_connection()
    greivances = conn.execute('SELECT * FROM greivances').fetchall()
    conn.close()
    return render_template('greivances.html', greivances=greivances)
@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    greivance = get_greivance(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM greivances WHERE ID = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(render_template('greivances.html'))

@app.route('/login', methods=('GET', 'POST'))
def login():
    conn = get_db_connection()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None;
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return render_template("greivances.html")

        flash(error)

    return render_template('login.html')

@app.before_request
def load_logged_in_user():
    conn = get_db_connection()
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = conn.execute('SELECT * FROM users WHERE id= ?', (user_id,)).fetchone()

@app.route('/logout', methods=('POST',))
def logout():
    session.clear()
    return render_template('index.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    conn = get_db_connection()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, generate_password_hash(password)),)
                conn.commit()
            except conn.IntegrityError:
                error = f'User {username} is already registered.'

            flash(error)

    return render_template('login.html')
