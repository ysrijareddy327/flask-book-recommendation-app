from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "books.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, default=0.0)

# Initialize DB and add sample books
def init_db():
    db.create_all()
    if not Book.query.first():
        sample_books = [
            Book(title="The Hobbit", genre="Fantasy", rating=4.8),
            Book(title="Harry Potter", genre="Fantasy", rating=4.9),
            Book(title="The Martian", genre="Science Fiction", rating=4.6),
            Book(title="Dune", genre="Science Fiction", rating=4.7),
            Book(title="Pride and Prejudice", genre="Romance", rating=4.5),
            Book(title="The Notebook", genre="Romance", rating=4.3),
            Book(title="To Kill a Mockingbird", genre="Classic", rating=4.9),
            Book(title="1984", genre="Classic", rating=4.8),
        ]
        db.session.add_all(sample_books)
        db.session.commit()

# Home page
@app.route("/", methods=["GET", "POST"])
def index():
    suggestions = []
    if request.method == "POST":
        genres = request.form.getlist("genre")
        search = request.form.get("search", "").lower()
        query = Book.query
        if genres:
            query = query.filter(Book.genre.in_(genres))
        if search:
            query = query.filter(Book.title.ilike(f"%{search}%"))
        suggestions = query.all()
    return render_template("index.html", suggestions=suggestions)

# Random book
@app.route("/random")
def random_book():
    books = Book.query.all()
    book = random.choice(books) if books else None
    return render_template("random.html", book=book)

# Add to favorites
@app.route("/favorite/<int:book_id>")
def favorite(book_id):
    if "favorites" not in session:
        session["favorites"] = []
    if book_id not in session["favorites"]:
        session["favorites"].append(book_id)
    return redirect(url_for("favorites"))

# Show favorites
@app.route("/favorites")
def favorites():
    fav_books = Book.query.filter(Book.id.in_(session.get("favorites", []))).all()
    return render_template("favorites.html", books=fav_books)

# Add new book
@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        rating = float(request.form["rating"])
        new_book = Book(title=title, genre=genre, rating=rating)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add_book.html")

# Run app
if __name__ == "__main__":
    with app.app_context():
        init_db()  # Initialize database inside application context
    app.run(debug=True)
