from flask import Flask, render_template, request, redirect, abort
import sqlite3

DATABASE = 'greivances.db'

app = Flask(__name__)

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
        
