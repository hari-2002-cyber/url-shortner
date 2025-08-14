from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import string, random

app = Flask(__name__)
app.secret_key = "mysecret"

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Database model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(6), unique=True, nullable=False)

# Create DB tables at startup
with app.app_context():
    db.create_all()

# Generate short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form["url"]

        if not long_url:
            flash("Please enter a URL", "error")
            return redirect(url_for("index"))

        # Check if already exists
        existing = URL.query.filter_by(original_url=long_url).first()
        if existing:
            short_code = existing.short_code
        else:
            short_code = generate_short_code()
            while URL.query.filter_by(short_code=short_code).first():
                short_code = generate_short_code()

            new_url = URL(original_url=long_url, short_code=short_code)
            db.session.add(new_url)
            db.session.commit()

        short_url = request.host_url + short_code
        return render_template("index.html", short_url=short_url)

    return render_template("index.html")

@app.route("/<short_code>")
def redirect_to_url(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first_or_404()
    return redirect(url_entry.original_url)

if __name__ == "__main__":
    app.run(debug=True)
