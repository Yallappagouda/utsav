from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# --- User Model ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))  # For demo only, plaintext

    def get_id(self):
        return str(self.id)

# --- User Loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Mock Vendor Data ---
vendors = [
    {"name": "Delight Caterers", "type": "Catering", "location": "Bangalore", "price": 50000, "rating": 4.8},
    {"name": "Snap Photography", "type": "Photography", "location": "Bangalore", "price": 25000, "rating": 4.5},
    {"name": "Star Events", "type": "Venue", "location": "Bangalore", "price": 100000, "rating": 4.7},
    {"name": "Joy DJ", "type": "Music", "location": "Bangalore", "price": 20000, "rating": 4.4},
    {"name": "Elite Decor", "type": "Decoration", "location": "Bangalore", "price": 30000, "rating": 4.9},
    {"name": "Taste Buds", "type": "Catering", "location": "Mumbai", "price": 45000, "rating": 4.2},
    {"name": "Mumbai Moments", "type": "Photography", "location": "Mumbai", "price": 22000, "rating": 4.3},
]

event_vendor_types = {
    "Wedding": ["Venue", "Catering", "Photography", "Music", "Decoration"],
    "Birthday": ["Venue", "Catering", "Music", "Decoration"],
    "Corporate": ["Venue", "Catering", "Photography"]
}

planning_steps = [
    "Book your venue early.",
    "Confirm your caterer and menu.",
    "Hire a photographer.",
    "Arrange music/DJ.",
    "Finalize decoration theme and vendor."
]

fun_messages = [
    "Your event is on track to be legendary! 🎉",
    "Your guests are in for a treat! 🍽️📸",
    "These vendors are a perfect match for your special day! 💍",
    "Your event will be the talk of the town! 🏆"
]

def score_vendor(vendor, avg_budget):
    rating_score = vendor["rating"] * 20
    budget_score = max(0, 100 - abs(vendor["price"] - avg_budget) / avg_budget * 100)
    bonus = 10 if vendor["rating"] >= 4.8 else 0
    return round(rating_score * 0.7 + budget_score * 0.3 + bonus, 2)

def match_score(vendor, avg_budget):
    rating_part = (vendor["rating"] / 5) * 50
    price_part = max(0, 30 - abs(vendor["price"] - avg_budget) / avg_budget * 30)
    bonus_part = 10 if vendor["type"] == "Decoration" else 0
    fun_bonus = random.randint(0, 10)
    return round(rating_part + price_part + bonus_part + fun_bonus, 2)

def ascii_bar(value, max_value=100, bar_length=10):
    proportion = min(float(value) / max_value, 1.0)
    filled = int(round(bar_length * proportion))
    empty = bar_length - filled
    percent = int(round(100 * proportion))
    return f"[{'#' * filled}{' ' * empty}] {percent}%"

app.jinja_env.filters['ascii_bar'] = ascii_bar

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    recommendations = {}
    total_spent = 0
    remaining = 0
    event_type = ""
    location = ""
    budget = 0
    filtered_vendors = []
    if request.method == "POST":
        event_type = request.form["event_type"].title()
        location = request.form["location"].title()
        try:
            budget = int(request.form["budget"])
        except:
            budget = 0

        needed_types = event_vendor_types.get(event_type, [])
        filtered_vendors = [
            v for v in vendors
            if v["location"] == location and v["type"] in needed_types
        ]
        avg_budget_per_vendor = budget // len(needed_types) if needed_types else budget

        scored_vendors = []
        for v in filtered_vendors:
            v = v.copy()
            v["score"] = score_vendor(v, avg_budget_per_vendor)
            v["match_score"] = match_score(v, avg_budget_per_vendor)
            scored_vendors.append(v)
        scored_vendors.sort(key=lambda x: x["score"], reverse=True)

        for vendor_type in needed_types:
            candidates = [v for v in scored_vendors if v["type"] == vendor_type]
            if candidates:
                recommendations[vendor_type] = candidates[0]
        total_spent = sum(v['price'] for v in recommendations.values()) if recommendations else 0
        remaining = budget - total_spent

        return render_template(
            "result.html",
            event_type=event_type,
            location=location,
            budget=budget,
            recommendations=recommendations,
            planning_steps=planning_steps,
            fun_message=random.choice(fun_messages),
            total_spent=total_spent,
            remaining=remaining,
            filtered_vendors=scored_vendors
        )
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
        else:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# --- Download Route (previous export feature) ---
from flask import send_file
import io

@app.route("/download", methods=["POST"])
@login_required
def download():
    event_type = request.form.get("event_type")
    location = request.form.get("location")
    budget = int(request.form.get("budget", 0))
    total_spent = int(request.form.get("total_spent", 0))
    remaining = int(request.form.get("remaining", 0))
    recommendations = []
    for key in request.form:
        if key.startswith('vendor_'):
            recommendations.append(request.form.get(key))

    content = []
    content.append("===== Event Planning AI Recommendation =====")
    content.append(f"Event Type: {event_type}")
    content.append(f"Location: {location}")
    content.append(f"Total Budget: ₹{budget}")
    content.append(f"Budget Used: ₹{total_spent}")
    content.append(f"Budget Remaining: ₹{remaining}\n")
    content.append("Recommended Vendors:")
    for line in recommendations:
        content.append(line)
    content.append("\nThank you for using Event Vendor Recommendation AI!")
    output = "\n".join(content)

    buffer = io.BytesIO()
    buffer.write(output.encode('utf-8'))
    buffer.seek(0)
    return send_file(buffer,
                     as_attachment=True,
                     download_name="event_recommendations.txt",
                     mimetype="text/plain")

if __name__ == "__main__":
    # Create DB if not exists
    if not os.path.exists("users.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)