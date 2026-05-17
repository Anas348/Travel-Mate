from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="traveluser",
    password="",
    database="smart_travel"
)

# ✅ FIX: buffered cursor to prevent "Unread result found"
cursor = db.cursor(dictionary=True, buffered=True)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- HOTEL SEARCH ----------------
@app.route('/hotels')
def hotels():
    city = request.args.get('city')
    price = request.args.get('price')
    rating = request.args.get('rating')

    query = "SELECT * FROM Hotel WHERE 1=1"
    params = []

    if city:
        query += " AND city LIKE %s"
        params.append(f"%{city}%")

    if price:
        query += " AND price_per_night <= %s"
        params.append(price)

    if rating:
        query += " AND rating >= %s"
        params.append(rating)

    cursor.execute(query, tuple(params))
    hotels = cursor.fetchall()

    return render_template('hotels.html', hotels=hotels)

# ---------------- HOTEL DETAIL ----------------
@app.route('/hotel/<int:id>')
def hotel_detail(id):
    # hotel info
    cursor.execute("SELECT * FROM Hotel WHERE hotel_id=%s", (id,))
    hotel = cursor.fetchone()

    if not hotel:
        return "Hotel not found"

    # rooms
    cursor.execute("SELECT * FROM Room WHERE hotel_id=%s", (id,))
    rooms = cursor.fetchall()

    # reviews
    cursor.execute("""
        SELECT r.*, u.name 
        FROM Review r
        JOIN Users u ON r.user_id = u.user_id
        WHERE r.hotel_id=%s
    """, (id,))
    reviews = cursor.fetchall()

    # attractions (based on city)
    cursor.execute("""
        SELECT * FROM Attraction
        WHERE location = %s
    """, (hotel['city'],))
    attractions = cursor.fetchall()

    return render_template(
        'hotel_detail.html',
        hotel=hotel,
        rooms=rooms,
        reviews=reviews,
        attractions=attractions
    )

# ---------------- ADD TO FAVOURITE ----------------
@app.route('/favourite', methods=['POST'])
def favourite():
    user_id = 1
    hotel_id = request.form.get('hotel_id')

    # prevent duplicates
    cursor.execute("""
        SELECT * FROM Favourite
        WHERE user_id=%s AND hotel_id=%s
    """, (user_id, hotel_id))

    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO Favourite (user_id, hotel_id)
            VALUES (%s, %s)
        """, (user_id, hotel_id))
        db.commit()

    return redirect(request.referrer)

# ---------------- VIEW FAVOURITES ----------------
@app.route('/favourites')
def favourites():
    user_id = 1

    cursor.execute("""
        SELECT Hotel.*
        FROM Favourite
        JOIN Hotel ON Favourite.hotel_id = Hotel.hotel_id
        WHERE Favourite.user_id = %s
    """, (user_id,))

    hotels = cursor.fetchall()

    return render_template('favourites.html', hotels=hotels)

# ---------------- REMOVE FAVOURITE ----------------
@app.route('/remove_favourite/<int:hotel_id>', methods=['POST'])
def remove_favourite(hotel_id):
    user_id = 1

    cursor.execute("""
        DELETE FROM Favourite
        WHERE user_id=%s AND hotel_id=%s
    """, (user_id, hotel_id))

    db.commit()

    return redirect('/favourites')
# ---------------- ADD REVIEW ----------------
@app.route('/review', methods=['POST'])
def review():
    user_id = 1

    hotel_id = request.form.get('hotel_id')
    rating = request.form.get('rating')
    comment = request.form.get('comment')

    cursor.execute("""
        INSERT INTO Review 
        (user_id, hotel_id, rating, comment, review_date)
        VALUES (%s, %s, %s, %s, CURDATE())
    """, (user_id, hotel_id, rating, comment))

    db.commit()

    return redirect(f'/hotel/{hotel_id}')

# ---------------- DESTINATIONS ----------------
@app.route('/destinations')
def destinations():
    cursor.execute("SELECT * FROM Destination")
    destinations = cursor.fetchall()

    return render_template('destinations.html', destinations=destinations)

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute("""
            SELECT * FROM Users 
            WHERE email=%s AND password=%s
        """, (email, password))

        user = cursor.fetchone()

        if user:
            return redirect('/')
        else:
            return "Invalid Credentials"

    return render_template('login.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("""
        INSERT INTO Users (name,email,password,role)
        VALUES (%s,%s,%s,'traveler')
    """, (name, email, password))

    db.commit()

    return redirect('/login')

# ---------------- EDIT REVIEW ----------------
@app.route('/edit_review/<int:id>', methods=['GET', 'POST'])
def edit_review(id):

    if request.method == 'POST':

        rating = request.form.get('rating')
        comment = request.form.get('comment')

        cursor.execute("""
            UPDATE Review
            SET rating=%s, comment=%s
            WHERE review_id=%s
        """, (rating, comment, id))

        db.commit()

        return redirect(request.form.get('redirect_url'))

    # GET REQUEST
    cursor.execute("SELECT * FROM Review WHERE review_id=%s", (id,))
    review = cursor.fetchone()

    return render_template('edit_review.html', review=review)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)