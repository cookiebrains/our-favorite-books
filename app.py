from flask import *
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, AddBookForm, EditForm
from flask_bootstrap import Bootstrap
from db_query import get_candidates, get_movie_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fave_books.db'
app.config['SECRET_KEY'] = 'He23HH12*&4'
db = SQLAlchemy(app)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    books = relationship("Books")


class Books(db.Model):
    __tablename__ = "books"
    id = db.Column('book_id', db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="books")
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Integer)
    review = db.Column(db.String(600))
    img_url = db.Column(db.String(400), nullable=False)


class ListBooksByUser(MethodView):
    template_file = 'index.html'

    def get(self):
        users = User.query.all()
        return render_template(self.template_file, users=users)


def seed_user_data():
    new_user = User(
        email="jo@mail.com",
        password="2345",
        name="Jo the Man"
    )
    db.session.add(new_user)
    db.session.commit()


def seed_book_data():
    new_book1 = Books(
        title="Cat in the Hat",
        user_id=1,
        description="A fun book about a cat doing crazy stuff.",
        rating=3,
        review="Not too bad, but kind of too long.",
        img_url="https://books.google.com/books/content?id=WUa82PCEzfkC&printsec=frontcover&img=1&zoom=5&source=gbs_api"

    )

    new_book2 = Books(
        title="Brothers K",
        user_id=1,
        description="A wild adventure",
        rating=4,
        review="Not too bad, but too long.",
        img_url="https://books.google.com/books/content?id=WUa82PCEzfkC&printsec=frontcover&img=1&zoom=5&source=gbs_api"
    )

    db.session.add(new_book1)
    db.session.add(new_book2)
    db.session.commit()


# @app.route('/')
# def home():
#     return render_template("index.html")


app.add_url_rule('/', view_func=ListBooksByUser.as_view("home"))


@app.route('/my_books', methods=["GET", "POST"])
def my_books():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        return render_template("my_books.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))

        # Password incorrect
        elif not email == user.email:
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))

        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add_book():
    add_form = AddBookForm()
    if add_form.validate_on_submit():
        new_title = add_form.title.data
        book_candidates = get_candidates(new_title)
        return render_template('select.html', options=book_candidates)
    return render_template('add_book.html', form=add_form)


@app.route("/delete/<int:id>")
def delete(id):
    # DELETE A RECORD BY ID
    book_to_delete = Books.query.get(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('my_books'))


@app.route("/find")
def find_book():
    book_api_id = request.args.get("id")
    if book_api_id:
        data = get_movie_data(book_api_id)
        print(data)
        new_book = Books(
            title=data["volumeInfo"]["title"],
            img_url=data["volumeInfo"]["imageLinks"]["thumbnail"],
            description=data["volumeInfo"]["description"],
            user_id=current_user.id
        )
        db.session.add(new_book)
        db.session.flush()
        db.session.refresh(new_book)
        new_id = new_book.id
        db.session.commit()
        return redirect(url_for('edit', id=new_id))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    edited_book = db.session.query(Books).filter_by(id=id).one()
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        new_rating = edit_form.rating.data
        new_review = edit_form.review.data
        edited_book.rating = new_rating
        edited_book.review = new_review
        db.session.add(edited_book)
        db.session.commit()
        return redirect(url_for('my_books'))
    return render_template('edit.html', form=edit_form, book=edited_book)


if __name__ == '__main__':
    app.run()
