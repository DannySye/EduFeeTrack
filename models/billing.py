import sqlite3
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password, role, student_id=None):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.student_id = student_id

def init_db():
    conn = sqlite3.connect('db/billing.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        tuition_amount REAL NOT NULL,
        additional_fees REAL DEFAULT 0,
        amount_paid REAL DEFAULT 0,
        due_date TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount REAL NOT NULL,
        payment_date TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        student_id TEXT,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )''')
    # Add default admin user
    c.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
              ('admin', 'admin123', 'admin'))
    conn.commit()
    conn.close()

def add_student(student_id, name, email, phone, tuition_amount, due_date):
    conn = sqlite3.connect('db/billing.db')
    c = conn.cursor()
    c.execute('INSERT INTO students (student_id, name, email, phone, tuition_amount, due_date) VALUES (?, ?, ?, ?, ?, ?)',
              (student_id, name, email, phone, tuition_amount, due_date))
    conn.commit()
    conn.close()

def add_fee(student_id, fee_type, amount, due_date):
    conn = sqlite3.connect('db/billing.db')
    c = conn.cursor()
    c.execute('UPDATE students SET additional_fees = additional_fees + ?, due_date = ? WHERE id = ?',
              (amount, due_date, student_id))
    conn.commit()
    conn.close()

def record_payment(student_id, amount, payment_date, payment_method):
    conn = sqlite3.connect('db/billing.db')
    c = conn.cursor()
    c.execute('UPDATE students SET amount_paid = amount_paid + ? WHERE id = ?', (amount, student_id))
    c.execute('INSERT INTO payments (student_id, amount, payment_date, payment_method) VALUES (?, ?, ?, ?)',
              (student_id, amount, payment_date, payment_method))
    conn.commit()
    conn.close()

def get_students():
    conn = sqlite3.connect('db/billing.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    students = c.execute('SELECT * FROM students').fetchall()
    conn.close()
    return students

def get_student_by_id(student_id):
    conn = sqlite3.connect('db/billing.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    student = c.execute('SELECT * FROM students WHERE student_id = ?', (student_id,)).fetchone()
    conn.close()
    return student

def get_payments(student_id):
    conn = sqlite3.connect('db/billing.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    payments = c.execute('SELECT * FROM payments WHERE student_id = ?', (student_id,)).fetchall()
    conn.close()
    return payments

def add_user(student_id, username, password, role):
    conn = sqlite3.connect('db/billing.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (username, password, role, student_id) VALUES (?, ?, ?, ?)',
              (username, password, role, student_id))
    conn.commit()
    conn.close()

def load_user(user_id):
    conn = sqlite3.connect('db/billing.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['password'], user['role'], user['student_id'])
    return None

def load_user_by_username(username):
    conn = sqlite3.connect('db/billing.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['password'], user['role'], user['student_id'])
    return None