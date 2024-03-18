import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Configure upload folder for candidate photos
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Model definitions
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(20), unique=True, nullable=False)
    voted = db.Column(db.Boolean, default=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    candidates = db.relationship('Candidate', backref='category', lazy='dynamic')

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# Routes
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'student_id' not in session and 'admin_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'student_login' in request.form:
            student_number = request.form['student_number']
            student = Student.query.filter_by(student_number=student_number).first()
            if student and not student.voted:
                session['student_id'] = student.id
                return redirect(url_for('vote'))
            else:
                flash('Invalid student number or already voted', 'error')
        elif 'admin_login' in request.form:
            username = request.form['username']
            password = request.form['password']
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session['admin_id'] = admin.id
                return redirect(url_for('admin_panel'))
            else:
                flash('Invalid admin credentials', 'error')

    return render_template('index.html')

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    student_id = session.get('student_id')
    categories = Category.query.all()

    if request.method == 'POST':
        candidate_id = request.form['candidate']
        candidate = Candidate.query.get(candidate_id)
        candidate.votes += 1
        student = Student.query.get(student_id)
        student.voted = True
        db.session.commit()
        return redirect(url_for('results'))

    return render_template('vote.html', categories=categories)

@app.route('/results')
@login_required
def results():
    categories = Category.query.all()
    return render_template('results.html', categories=categories)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    admin_id = session.get('admin_id')

    if request.method == 'POST':
        if request.form.get('add_candidate'):
            category_id = request.form['category']
            name = request.form['name']
            photo = request.files['photo']
            if photo:
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                candidate = Candidate(name, Category.query.get(category_id), filename)
                db.session.add(candidate)
                db.session.commit()
                flash('Candidate added successfully', 'success')
        elif request.form.get('delete_candidate'):
            candidate_id = request.form['candidate']
            candidate = Candidate.query.get(candidate_id)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], candidate.photo))
            db.session.delete(candidate)
            db.session.commit()
            flash('Candidate deleted successfully', 'success')

    categories = Category.query.all()
    candidates = Candidate.query.all()
    return render_template('admin.html', categories=categories, candidates=candidates)

# Initial setup
def init_app():
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            admin = Admin(username='admin', password_hash=bcrypt.generate_password_hash('password').decode('utf-8'))
            db.session.add(admin)
            db.session.commit()
        if not Category.query.first():
            categories = ['President', 'Vice President', 'Secretary', 'Treasurer']
            for category_name in categories:
                category = Category(name=category_name)
                db.session.add(category)
            db.session.commit()

if __name__ == '__main__':
    init_app()
    app.run(debug=True)