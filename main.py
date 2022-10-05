from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, UserMixin, login_required
import datetime as dt


current_year = dt.datetime.now().year

app = Flask(__name__)
app.config['SECRET_KEY'] = 'todo_list_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heading = db.Column(db.String(100), nullable=False)
    body = db.Column(db.String(250), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def HomePage():
    todos_list = TodoList.query.all()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Log In Must')
            return redirect(url_for('login'))

        new_todo = TodoList(
            heading=request.form.get('heading'),
            body=request.form.get('body')
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('HomePage'))

    return render_template('index.html',
                           current_year=current_year,
                           todos=todos_list,
                           current_user=current_user)


@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    if not current_user.is_authenticated:
        flash('Log In Must')
        return redirect(url_for('login'))

    todos_list = TodoList.query.all()
    todo = db.session.query(TodoList).get(todo_id)
    if request.method == 'POST':
        todo.heading = request.form.get('heading')
        todo.body = request.form.get('body')
        db.session.commit()
        return redirect(url_for('HomePage'))

    return render_template('edit.html',
                           todo=todo,
                           current_year=current_year)


@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    if not current_user.is_authenticated:
        flash('Log In Must')
        return redirect(url_for('login'))

    todo = db.session.query(TodoList).get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('HomePage'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')

        user = db.session.query(User).filter_by(email=email).first()
        if user:
            flash('User with this email already exist. Log In instead.')
            return redirect(url_for('login'))

        new_user = User(
            name=request.form.get('name'),
            email=request.form.get('email'),
            password=request.form.get('password'),
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('HomePage'))

    return render_template('register.html',
                           current_user=current_user,
                           current_year=current_year)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User does not exist.')
            return redirect(url_for('login'))

        if user.email == email and user.password == password:
            login_user(user)
            return redirect(url_for('HomePage'))
        else:
            flash('Invalid Credentials')
            return redirect(url_for('login'))

    return render_template('login.html',
                           current_user=current_user,
                           current_year=current_year)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('HomePage'))


if __name__ == "__main__":
    app.run(debug=True)
