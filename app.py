from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

    
def get_db():
    conn = sqlite3.connect('junto.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            datetime TEXT NOT NULL,
            spots INTEGER NOT NULL,
            host TEXT NOT NULL
        )
    ''')
    # Seed some dummy activities
    existing = conn.execute('SELECT COUNT(*) FROM activities').fetchone()[0]
    if existing == 0:
        dummy = [
            ('Morning Run at Central Park', 'Sports & Fitness', 'Central Park', 'Tomorrow 7:00 AM', 5, 'Alex'),
            ('Study Session - Calculus', 'Study/Cowork', 'City Library', 'Today 4:00 PM', 4, 'Priya'),
            ('Startup Networking Mixer', 'Networking/Career', 'WeWork Downtown', 'Friday 6:00 PM', 20, 'James'),
            ('Chill Hangout + Board Games', 'Socialize/Hangout', 'Rooftop Cafe', 'Saturday 3:00 PM', 8, 'Sara'),
            ('Launch a Photography Club', 'Start a Club', 'Online + Local', 'Sunday 5:00 PM', 15, 'Manav'),
        ]
        conn.executemany('INSERT INTO activities (title, category, location, datetime, spots, host) VALUES (?,?,?,?,?,?)', dummy)
    conn.commit()
    conn.close()
    
with app.app_context():
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/waitlist', methods=['POST'])
def waitlist():
    email = request.form.get('email')
    if email:
        try:
            conn = get_db()
            conn.execute('INSERT INTO waitlist (email) VALUES (?)', (email,))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            pass  # Email already exists
    return redirect(url_for('index', joined='true'))

@app.route('/feed')
def feed():
    conn = get_db()
    activities = conn.execute('SELECT * FROM activities').fetchall()
    conn.close()
    return render_template('feed.html', activities=activities)

if __name__ == '__main__':
    init_db()
    import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)

