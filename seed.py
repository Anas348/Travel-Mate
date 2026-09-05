"""
Create tables (if missing) and load sample data.

Works against whatever DATABASE_URL points at -- SQLite, PostgreSQL, MySQL --
because it goes through the SQLAlchemy models in models.py rather than raw,
dialect-specific SQL.

Usage:
    python seed.py            # create tables + seed sample data (skips rows that already exist)
    python seed.py --reset    # drop every table and start clean, then seed

See README.md, section "Adding more data", for how to add your own rows
on top of this instead of editing this file.
"""
import sys
from datetime import date

from werkzeug.security import generate_password_hash

from app import app
from models import db, User, Hotel, Room, Destination, Attraction, Review, Amenity, HotelAmenity


def seed():
    with app.app_context():
        if "--reset" in sys.argv:
            db.drop_all()
        db.create_all()

        if User.query.first():
            print("Database already has data — skipping seed. Run with --reset to start over.")
            return

        users = [
            User(name="Anas Malik", email="anas@gmail.com",
                 password_hash=generate_password_hash("1234"), role="traveler"),
            User(name="Sara Khan", email="sara@gmail.com",
                 password_hash=generate_password_hash("1234"), role="traveler"),
            User(name="Ali Raza", email="ali@gmail.com",
                 password_hash=generate_password_hash("1234"), role="admin"),
        ]
        db.session.add_all(users)
        db.session.commit()
        anas, sara, ali = users

        hotels_data = [
            ("Pearl Continental", "Lahore", "Mall Road", 20000, 4.5,
             "A landmark five-star stay in the heart of Lahore, close to the old city's food streets.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Minar-e-Pakistan%201%20lahore.JPG"),
            ("Avari Hotel", "Lahore", "Shahrah-e-Quaid-e-Azam", 18000, 4.2,
             "A long-standing business favourite on Lahore's main boulevard.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Minar-e-Pakistan%202%20lahore.JPG"),
            ("Serena Hotel", "Islamabad", "Sector G-5", 25000, 4.7,
             "Islamabad's most polished address, set against the Margalla Hills.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Islamabad%20skyline.jpg"),
            ("Luxus Grand", "Lahore", "Egerton Road", 15000, 4.3,
             "A modern mid-range hotel a short walk from Lahore's main galleries.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Bahria%20Town%20Lahore%20Pakistan.jpg"),
            ("Hunza Resort", "Hunza", "Karimabad", 12000, 4.6,
             "Wake up to Rakaposhi from your balcony in the heart of Karimabad.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Beauty%20of%20Hunza%20Valley%2001.jpg"),
            ("Skardu Palace", "Skardu", "Near Airport Road", 14000, 4.4,
             "The easiest base for Deosai and the Skardu valley lakes.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Satpara%20Lake%2CSkardu%20%2CGilgit%20and%20Baltistan%2C%20Pakistan.JPG"),
        ]
        hotels = []
        for name, city, address, price, rating, desc, img in hotels_data:
            hotels.append(Hotel(name=name, city=city, address=address, price_per_night=price,
                                 rating=rating, description=desc, image_url=img, owner_id=ali.id))
        db.session.add_all(hotels)
        db.session.commit()

        rooms_data = [
            (0, "Single", 8000), (0, "Double", 12000),
            (1, "Single", 7000), (1, "Deluxe", 11000),
            (2, "Suite", 20000), (2, "Double", 15000),
            (3, "Single", 6000), (3, "Double", 10000),
            (4, "Deluxe", 9000), (4, "Suite", 13000),
            (5, "Single", 7500), (5, "Deluxe", 12000),
        ]
        for hotel_idx, room_type, price in rooms_data:
            db.session.add(Room(hotel_id=hotels[hotel_idx].id, room_type=room_type, price=price))

        amenity_names = ["WiFi", "Swimming Pool", "Parking", "Gym", "Restaurant", "Room Service"]
        amenities = [Amenity(name=a) for a in amenity_names]
        db.session.add_all(amenities)
        db.session.commit()
        amenity_by_name = {a.name: a for a in amenities}

        hotel_amenities = [
            (0, ["WiFi", "Swimming Pool", "Restaurant"]),
            (1, ["WiFi", "Parking"]),
            (2, ["WiFi", "Swimming Pool", "Gym", "Restaurant"]),
            (3, ["WiFi", "Room Service"]),
            (4, ["WiFi", "Parking", "Restaurant"]),
            (5, ["WiFi", "Gym"]),
        ]
        for hotel_idx, names in hotel_amenities:
            for n in names:
                db.session.add(HotelAmenity(hotel_id=hotels[hotel_idx].id, amenity_id=amenity_by_name[n].id))

        destinations_data = [
            ("Hunza Valley", "Hunza", "Famous for mountains and scenic beauty.", "Best time: May to September.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Hunza%20Valley%20HDR.jpg"),
            ("Skardu Valley", "Skardu", "Lakes, mountains, and a cold desert landscape.", "Carry warm clothes.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Cold%20Desert%20Skardu.JPG"),
            ("Murree Hills", "Murree", "A popular hill station near Islamabad.", "Avoid weekends due to rush.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/A%20beautiful%20view%20of%20Murree%2C%20Pakistan.jpg"),
            ("Fairy Meadows", "Gilgit", "A base camp view of Nanga Parbat.", "Requires a jeep ride from Raikot Bridge.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Nanga%20Parbat%20%28Fairy%20Meadows%29.jpg"),
            ("Swat Valley", "Swat", "Often called the Switzerland of Pakistan.", "Visit in spring for the greenery.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Malam%20Jabba%2C%20Swat%20Valley%2C%20Pakistan.jpg"),
        ]
        destinations = []
        for name, city, desc, tips, img in destinations_data:
            destinations.append(Destination(name=name, city=city, description=desc, travel_tips=tips, image_url=img))
        db.session.add_all(destinations)
        db.session.commit()

        attractions_data = [
            (0, "Attabad Lake", "A turquoise lake formed by a 2010 landslide.", "Hunza"),
            (0, "Baltit Fort", "A centuries-old fort overlooking Karimabad.", "Hunza"),
            (1, "Shangrila Resort", "A lakeside resort known as 'heaven on earth'.", "Skardu"),
            (2, "Mall Road", "Murree's central shopping and walking street.", "Murree"),
            (3, "Nanga Parbat View", "A viewpoint facing the world's 9th-highest peak.", "Fairy Meadows"),
            (4, "Malam Jabba", "Pakistan's best-known ski resort.", "Swat"),
        ]
        for dest_idx, name, desc, location in attractions_data:
            db.session.add(Attraction(destination_id=destinations[dest_idx].id, name=name,
                                       description=desc, location=location))

        reviews_data = [
            (anas, 0, 5, "Amazing stay and great service!"),
            (sara, 0, 4, "Very comfortable rooms."),
            (anas, 1, 4, "Nice location but a bit expensive."),
            (sara, 2, 5, "Luxury experience!"),
            (anas, 4, 5, "Beautiful scenery and peaceful."),
        ]
        for user, hotel_idx, rating, comment in reviews_data:
            db.session.add(Review(user_id=user.id, hotel_id=hotels[hotel_idx].id, rating=rating,
                                   comment=comment, review_date=date.today()))

        db.session.commit()
        print("Seeded 3 users, 6 hotels, 12 rooms, 5 destinations, 6 attractions, 5 reviews.")
        print("Demo login: anas@gmail.com / 1234  (traveler)   ali@gmail.com / 1234  (admin)")


if __name__ == "__main__":
    seed()
