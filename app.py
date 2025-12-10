from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from functools import wraps                  # DITAMBAHKAN
from werkzeug.security import generate_password_hash, check_password_hash   # DITAMBAHKAN
# import os
# import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = " secret123"    	# DITAMBAHKAN
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

class User(db.Model):                     	# DITAMBAHKAN
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

def login_required(f):                 	# DITAMBAHKAN
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:   	# DITAMBAHKAN
            flash("Silakan login dahulu.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@login_required 
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route("/register", methods=["GET", "POST"])    # DITAMBAHKAN
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])   # DITAMBAHKAN
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registrasi berhasil!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])    # DITAMBAHKAN
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):   # DITAMBAHKAN
            session["user_id"] = user.id    	# DITAMBAHKAN
            session["username"] = user.username # DITAMBAHKAN
            return redirect(url_for("index"))
        flash("Username atau password salah.", "danger")
    return render_template("login.html")


@app.route("/logout")                 	# DITAMBAHKAN
def logout():
    session.clear()                   	# DITAMBAHKAN
    return redirect(url_for("login"))

@app.route('/add', methods=['POST'])
@login_required 
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    # RAW Query
    db.session.execute(
        text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
        {'name': name, 'age': age, 'grade': grade}
    )
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>') 
@login_required 
def delete_student(id):
    # RAW Query
    # db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    # db.session.commit()
    db.session.execute(text("DELETE FROM student WHERE id=:id"),{'id': id})
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required 
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # RAW Query
        # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.execute(text("UPDATE student SET name=:name, age=:age, grade=:grade WHERE id=:id"),
        {'name': name, 'age': age, 'grade': grade, 'id': id})
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        if not student : return redirect(url_for('index'))
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=False)

