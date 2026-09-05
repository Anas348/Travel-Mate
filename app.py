from functools import wraps
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Hotel, Room, Favourite, Destination, Attraction, Review, Amenity

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to do that.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    return {"current_user": current_user()}


# A small, fixed palette of gradients standing in for photography -- picked
# deterministically per city name so the same place always looks the same.
_CITY_GRADIENTS = [
    "linear-gradient(135deg, #16233a, #2f6f62)",
    "linear-gradient(135deg, #204d43, #16233a)",
    "linear-gradient(135deg, #16233a, #a8452f)",
    "linear-gradient(135deg, #2c3e58, #b9840f)",
    "linear-gradient(135deg, #234f45, #223349)",
    "linear-gradient(135deg, #16233a, #5c6270)",
]


@app.template_filter("city_gradient")
def city_gradient(city):
    if not city:
        return _CITY_GRADIENTS[0]
    return _CITY_GRADIENTS[sum(ord(c) for c in city) % len(_CITY_GRADIENTS)]


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    featured_hotels = Hotel.query.order_by(Hotel.rating.desc()).limit(3).all()
    featured_destinations = Destination.query.limit(4).all()
    return render_template(
        "index.html",
        featured_hotels=featured_hotels,
        featured_destinations=featured_destinations,
        total_hotels=Hotel.query.count(),
        total_destinations=Destination.query.count(),
    )


# ---------------------------------------------------------------------------
# Hotels
# ---------------------------------------------------------------------------

@app.route("/hotels")
def hotels():
    city = request.args.get("city", "").strip()
    price = request.args.get("price", "").strip()
    rating = request.args.get("rating", "").strip()

    query = Hotel.query
    if city:
        query = query.filter(Hotel.city.ilike(f"%{city}%"))
    if price:
        try:
            query = query.filter(Hotel.price_per_night <= float(price))
        except ValueError:
            pass
    if rating:
        try:
            query = query.filter(Hotel.rating >= float(rating))
        except ValueError:
            pass

    hotel_list = query.order_by(Hotel.rating.desc()).all()
    favourite_ids = set()
    if current_user():
        favourite_ids = {f.hotel_id for f in current_user().favourites}

    return render_template(
        "hotels.html",
        hotels=hotel_list,
        favourite_ids=favourite_ids,
        filters={"city": city, "price": price, "rating": rating},
    )


@app.route("/hotel/<int:hotel_id>")
def hotel_detail(hotel_id):
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel:
        abort(404)

    attractions = (
        Attraction.query.filter(Attraction.location.ilike(f"%{hotel.city}%")).all()
    )
    reviews = (
        Review.query.filter_by(hotel_id=hotel.id).order_by(Review.review_date.desc()).all()
    )
    is_favourite = False
    if current_user():
        is_favourite = any(f.hotel_id == hotel.id for f in current_user().favourites)

    return render_template(
        "hotel_detail.html",
        hotel=hotel,
        rooms=hotel.rooms,
        reviews=reviews,
        attractions=attractions,
        is_favourite=is_favourite,
    )


@app.route("/favourite", methods=["POST"])
@login_required
def favourite():
    hotel_id = request.form.get("hotel_id", type=int)
    hotel = db.session.get(Hotel, hotel_id)
    if not hotel:
        abort(404)

    exists = Favourite.query.filter_by(user_id=session["user_id"], hotel_id=hotel_id).first()
    if not exists:
        db.session.add(Favourite(user_id=session["user_id"], hotel_id=hotel_id))
        db.session.commit()
        flash(f"Added {hotel.name} to your favourites.", "success")

    return redirect(request.referrer or url_for("hotels"))


@app.route("/favourites")
@login_required
def favourites():
    favs = Favourite.query.filter_by(user_id=session["user_id"]).all()
    hotel_list = [f.hotel for f in favs]
    return render_template("favourites.html", hotels=hotel_list)


@app.route("/remove_favourite/<int:hotel_id>", methods=["POST"])
@login_required
def remove_favourite(hotel_id):
    Favourite.query.filter_by(user_id=session["user_id"], hotel_id=hotel_id).delete()
    db.session.commit()
    return redirect(request.referrer or url_for("favourites"))


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

@app.route("/review", methods=["POST"])
@login_required
def review():
    hotel_id = request.form.get("hotel_id", type=int)
    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()

    if not (hotel_id and rating and comment):
        flash("Please fill in a rating and a comment.", "error")
        return redirect(request.referrer or url_for("home"))

    db.session.add(
        Review(user_id=session["user_id"], hotel_id=hotel_id, rating=rating,
               comment=comment, review_date=date.today())
    )
    db.session.commit()
    flash("Thanks — your review is live.", "success")
    return redirect(url_for("hotel_detail", hotel_id=hotel_id))


@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    review_obj = db.session.get(Review, review_id)
    if not review_obj:
        abort(404)
    if review_obj.user_id != session["user_id"] and not current_user().is_admin:
        abort(403)

    if request.method == "POST":
        review_obj.rating = request.form.get("rating", type=int)
        review_obj.comment = request.form.get("comment", "").strip()
        db.session.commit()
        flash("Review updated.", "success")
        return redirect(request.form.get("redirect_url") or url_for("hotel_detail", hotel_id=review_obj.hotel_id))

    return render_template("edit_review.html", review=review_obj)


# ---------------------------------------------------------------------------
# Destinations
# ---------------------------------------------------------------------------

@app.route("/destinations")
def destinations():
    destination_list = Destination.query.all()
    return render_template("destinations.html", destinations=destination_list)


@app.route("/destination/<int:destination_id>")
def destination_detail(destination_id):
    destination = db.session.get(Destination, destination_id)
    if not destination:
        abort(404)
    return render_template("destination_detail.html", destination=destination)


# ---------------------------------------------------------------------------
# Add listings ("if other users want to add too")
# ---------------------------------------------------------------------------

@app.route("/add-hotel", methods=["GET", "POST"])
@login_required
def add_hotel():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        city = request.form.get("city", "").strip()
        address = request.form.get("address", "").strip()
        description = request.form.get("description", "").strip()
        image_url = request.form.get("image_url", "").strip()
        price = request.form.get("price_per_night", type=float)

        if not (name and city and price):
            flash("Name, city, and price per night are required.", "error")
            return render_template("add_hotel.html", form=request.form)

        hotel = Hotel(
            name=name, city=city, address=address, description=description,
            image_url=image_url, price_per_night=price, rating=0, owner_id=session["user_id"],
        )
        db.session.add(hotel)
        db.session.commit()

        room_types = request.form.getlist("room_type[]")
        room_prices = request.form.getlist("room_price[]")
        for r_type, r_price in zip(room_types, room_prices):
            if r_type.strip() and r_price.strip():
                db.session.add(Room(hotel_id=hotel.id, room_type=r_type.strip(), price=float(r_price)))
        db.session.commit()

        flash(f"{hotel.name} is live on TravelMate.", "success")
        return redirect(url_for("hotel_detail", hotel_id=hotel.id))

    return render_template("add_hotel.html", form={})


@app.route("/add-destination", methods=["GET", "POST"])
@login_required
def add_destination():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        city = request.form.get("city", "").strip()
        description = request.form.get("description", "").strip()
        image_url = request.form.get("image_url", "").strip()
        travel_tips = request.form.get("travel_tips", "").strip()

        if not (name and city):
            flash("Name and city are required.", "error")
            return render_template("add_destination.html", form=request.form)

        destination = Destination(
            name=name, city=city, description=description, image_url=image_url,
            travel_tips=travel_tips, added_by=session["user_id"],
        )
        db.session.add(destination)
        db.session.commit()

        attraction_names = request.form.getlist("attraction_name[]")
        for a_name in attraction_names:
            if a_name.strip():
                db.session.add(Attraction(destination_id=destination.id, name=a_name.strip(), location=city))
        db.session.commit()

        flash(f"{destination.name} has been added.", "success")
        return redirect(url_for("destination_detail", destination_id=destination.id))

    return render_template("add_destination.html", form={})


@app.route("/my-listings")
@login_required
def my_listings():
    my_hotels = Hotel.query.filter_by(owner_id=session["user_id"]).all()
    my_destinations = Destination.query.filter_by(added_by=session["user_id"]).all()
    return render_template("my_listings.html", hotels=my_hotels, destinations=my_destinations)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            flash(f"Welcome back, {user.name.split()[0]}.", "success")
            return redirect(request.args.get("next") or url_for("home"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not (name and email and password):
        flash("Please fill in every field to register.", "error")
        return redirect(url_for("login"))

    if User.query.filter_by(email=email).first():
        flash("An account with that email already exists.", "error")
        return redirect(url_for("login"))

    user = User(name=name, email=email, password_hash=generate_password_hash(password), role="traveler")
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    session["user_name"] = user.name
    flash("Account created — you're in.", "success")
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "success")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


@app.errorhandler(403)
def forbidden(_error):
    return render_template("403.html"), 403


if __name__ == "__main__":
    app.run(debug=True)
