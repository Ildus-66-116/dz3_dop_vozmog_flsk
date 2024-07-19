from flask import Flask, render_template, request, redirect, session, url_for
from flask_wtf import CSRFProtect
from models import User, db
from forms import RegisterForm
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase_users_dz.db'
db.init_app(app)

app.config['SECRET_KEY'] = b'a552cc79063c38bb5cf59769256b7a8c47ec9b98decd4eda60c2561c1f5b7eff'
csrf = CSRFProtect(app)


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print('OK')


@app.route('/')
def base():
    message = session.pop('message', None)
    errors = session.pop('errors', None)
    return render_template('base.html', message=message, errors=errors)


def users_add(username, firstname, lastname, email, password):
    user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=password)
    db.session.add(user)
    db.session.commit()


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = form.password.data.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)
        try:
            users_add(username, firstname, lastname, email, hashed_password)
        except Exception:
            session['errors'] = f'Ошибка пользователь {username} уже существует'
            return redirect(url_for('base'))
        session['message'] = f'Регистрация {username} прошла успешно!'
        return redirect(url_for('base'))
    return render_template('register.html', form=form)


@app.get('/users/')
def get_users():
    users = User.query.all()
    return f'{list(users)}'


if __name__ == '__main__':
    app.run(debug=True)
