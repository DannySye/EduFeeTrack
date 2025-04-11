from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'danielmwiine2025@gmail.com'
app.config['MAIL_PASSWORD'] = 'dxxd vcgi ennb fsxt'
app.config['MAIL_DEFAULT_SENDER'] = 'danielmwiine2025@gmail.com'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)

def format_ugx(amount):
    return f"UGX {amount:,.2f}"

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    other_names = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(200))
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    program = db.Column(db.String(100))
    semester = db.Column(db.String(20))
    year = db.Column(db.Integer)
    total_due = db.Column(db.Float, default=0.0)
    total_paid = db.Column(db.Float, default=0.0)
    payments = db.relationship('Payment', backref='student', lazy=True)
    fees = db.relationship('Fee', backref='student', lazy=True)

    def balance(self):
        return self.total_due - self.total_paid

    def is_overdue(self):
        return self.balance() > 0

    def __repr__(self):
        return f'<Student {self.first_name} {self.other_names} ({self.registration_number})>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))

class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

class FeeFine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fine_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    applied = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    with app.app_context():
        user_count = User.query.count()
    if request.method == 'POST':
        if 'create_user' in request.form and user_count == 0:
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                return 'Username already exists', 400
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('admin_dashboard'))
        else:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('login.html', error='Invalid username or password', user_count=user_count)
    return render_template('login.html', user_count=user_count)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/student_details')
@login_required
def student_details():
    students = Student.query.all()
    return render_template('student_details.html', students=students)

@app.route('/financial_details')
@login_required
def financial_details():
    students = Student.query.all()
    return render_template('financial_details.html', students=students, format_ugx=format_ugx)

@app.route('/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    if request.method == 'POST':
        if 'add_user' in request.form:
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
            else:
                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                flash('User added successfully', 'success')
        elif 'delete_user' in request.form:
            user_id = request.form['user_id']
            user = User.query.get(user_id)
            if user and user.id != current_user.id:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully', 'success')
            else:
                flash('Cannot delete yourself', 'danger')
    users = User.query.all()
    return render_template('user_management.html', users=users)

@app.route('/edufeetrack', methods=['GET', 'POST'])
@login_required
def edufeetrack():
    if request.method == 'POST':
        if 'set_semester' in request.form:
            semester_start = datetime.strptime(request.form['semester_start'], '%Y-%m-%d')
            with open('semester_start.txt', 'w') as f:
                f.write(semester_start.strftime('%Y-%m-%d'))
            flash('Semester start date set', 'success')
        elif 'add_fine' in request.form:
            fine_date = datetime.strptime(request.form['fine_date'], '%Y-%m-%dT%H:%M')
            amount = float(request.form['amount'])
            description = request.form['description']
            fine = FeeFine(fine_date=fine_date, amount=amount, description=description)
            db.session.add(fine)
            db.session.commit()
            flash('Fee fine added', 'success')
    
    semester_start = None
    try:
        with open('semester_start.txt', 'r') as f:
            semester_start = datetime.strptime(f.read(), '%Y-%m-%d')
    except FileNotFoundError:
        pass
    
    fines = FeeFine.query.all()
    return render_template('edufeetrack.html', semester_start=semester_start, fines=fines, format_ugx=format_ugx)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        registration_number = request.form['registration_number']
        if Student.query.filter_by(registration_number=registration_number).first():
            return render_template('add_student.html', error='Registration number already exists')
        new_student = Student(
            registration_number=registration_number,
            first_name=request.form['first_name'],
            other_names=request.form['other_names'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            program=request.form['program'],
            semester=request.form['semester'],
            year=int(request.form['year'])
        )
        db.session.add(new_student)
        db.session.commit()
        
        fee_descriptions = request.form.getlist('fee_description')
        fee_amounts = request.form.getlist('fee_amount')
        total_due = 0
        for desc, amt in zip(fee_descriptions, fee_amounts):
            if desc and amt:
                fee = Fee(student_id=new_student.id, description=desc, amount=float(amt))
                total_due += float(amt)
                db.session.add(fee)
        new_student.total_due = total_due
        db.session.commit()
        return redirect(url_for('financial_details'))
    return render_template('add_student.html')

@app.route('/add_payment/<registration_number>', methods=['GET', 'POST'])
@login_required
def add_payment(registration_number):
    student = Student.query.filter_by(registration_number=registration_number).first()
    if not student:
        return 'Student not found', 404
    if request.method == 'POST':
        amount = float(request.form['amount'])
        description = request.form['description']
        payment = Payment(student_id=student.id, amount=amount, description=description)
        student.total_paid += amount
        db.session.add(payment)
        db.session.commit()
        return redirect(url_for('financial_details'))
    return render_template('add_payment.html', student=student, format_ugx=format_ugx)

@app.route('/payment_history/<registration_number>')
@login_required
def payment_history(registration_number):
    student = Student.query.filter_by(registration_number=registration_number).first()
    if not student:
        return 'Student not found', 404
    payments = Payment.query.filter_by(student_id=student.id).all()
    fines = FeeFine.query.filter_by(applied=True).all()  # Fetch applied fines
    return render_template('payment_history.html', student=student, payments=payments, fines=fines, format_ugx=format_ugx)

@app.route('/download_payment_history/<registration_number>')
@login_required
def download_payment_history(registration_number):
    student = Student.query.filter_by(registration_number=registration_number).first()
    if not student:
        return 'Student not found', 404
    payments = Payment.query.filter_by(student_id=student.id).all()
    fines = FeeFine.query.filter_by(applied=True).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Payment History for {student.first_name} {student.other_names} ({student.registration_number})", styles['Title']))
    elements.append(Paragraph(f"Email: {student.email}", styles['Normal']))
    elements.append(Paragraph(f"Total Due: {format_ugx(student.total_due)} | Total Paid: {format_ugx(student.total_paid)} | Balance: {format_ugx(student.balance())}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Payments Table
    elements.append(Paragraph("Payments", styles['Heading2']))
    data = [['Date', 'Amount', 'Description']]
    for payment in payments:
        data.append([
            payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
            format_ugx(payment.amount),
            payment.description
        ])
    payment_table = Table(data)
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(payment_table)
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Fines Table
    elements.append(Paragraph("Applied Fines", styles['Heading2']))
    fine_data = [['Date', 'Amount', 'Description']]
    for fine in fines:
        fine_data.append([
            fine.fine_date.strftime('%Y-%m-%d %H:%M:%S'),
            format_ugx(fine.amount),
            fine.description
        ])
    fine_table = Table(fine_data)
    fine_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(fine_table)

    doc.build(elements)
    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename=payment_history_{student.registration_number}.pdf'}
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def edufeetrack_task():
    while True:
        with app.app_context():
            now = datetime.utcnow() + timedelta(hours=3)
            fines = FeeFine.query.filter_by(applied=False).all()
            students = Student.query.all()

            for fine in fines:
                if now >= fine.fine_date:
                    for student in students:
                        student.total_due += fine.amount
                    fine.applied = True
                    db.session.commit()

                time_to_fine = fine.fine_date - now
                days_to_fine = time_to_fine.days
                if days_to_fine in [7, 3, 1]:
                    for student in students:
                        if student.balance() > 0:
                            msg = Message(
                                subject=f"Upcoming Fee Fine Reminder - {days_to_fine} Days Left",
                                recipients=[student.email],
                                body=f"Dear {student.first_name},\n\nA fee fine of {format_ugx(fine.amount)} ({fine.description}) is due on {fine.fine_date.strftime('%Y-%m-%d %H:%M')}. Your current balance is {format_ugx(student.balance())}.\n\nRegards,\nEduFeeTrack System"
                            )
                            mail.send(msg)

            for student in students:
                if student.balance() > 0:
                    msg = Message(
                        subject="Outstanding Balance Reminder",
                        recipients=[student.email],
                        body=f"Dear {student.first_name},\n\nYour current balance of {format_ugx(student.balance())} remains unpaid.\n\nRegards,\nEduFeeTrack System"
                    )
                    mail.send(msg)

        time.sleep(60)

threading.Thread(target=edufeetrack_task, daemon=True).start()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)