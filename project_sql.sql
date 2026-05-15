CREATE DATABASE smart_travel;
USE smart_travel;

CREATE TABLE Users(
user_id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
email VARCHAR(100) UNIQUE NOT NULL,
password VARCHAR(100) NOT NULL,
role ENUM('traveler','admin') NOT NULL
);

CREATE TABLE Hotel(
hotel_id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
city VARCHAR(100),
address VARCHAR(255),
price_per_night DECIMAL(10,2),
rating DECIMAL(2,1),
owner_id INT,
FOREIGN KEY (owner_id) REFERENCES Users(user_id)
ON DELETE SET NULL
ON UPDATE CASCADE
);

CREATE TABLE Room(
room_id INT AUTO_INCREMENT PRIMARY KEY,
hotel_id INT,
room_type VARCHAR(50),
price DECIMAL(10,2),
availability_status BOOLEAN DEFAULT TRUE,
FOREIGN KEY (hotel_id) REFERENCES Hotel(hotel_id)
ON DELETE CASCADE
);

CREATE TABLE Booking(
booking_id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT,
room_id INT,
check_in_date DATE,
check_out_date DATE,
total_price DECIMAL(10,2),
FOREIGN KEY(user_id) REFERENCES Users(user_id)
ON DELETE CASCADE,
FOREIGN KEY (room_id) REFERENCES Room(room_id)
ON DELETE CASCADE
);

CREATE TABLE Destination(
destination_id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
city VARCHAR(100),
description TEXT,
travel_tips TEXT
);

CREATE TABLE Attraction(
attraction_id INT AUTO_INCREMENT PRIMARY KEY,
destination_id INT,
name VARCHAR(100),
description TEXT,
location VARCHAR(255),
FOREIGN KEY(destination_id) REFERENCES Destination(destination_id)
ON DELETE CASCADE
);

CREATE TABLE Review(
review_id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT,
hotel_id INT,
rating INT CHECK (rating BETWEEN 1 AND 5),
comment TEXT,
review_date DATE,
FOREIGN KEY (user_id) REFERENCES Users(user_id)
ON DELETE CASCADE,
FOREIGN KEY (hotel_id) REFERENCES Hotel(hotel_id)
ON DELETE CASCADE
);

CREATE TABLE Amenity(
amenity_id INT AUTO_INCREMENT PRIMARY KEY,
amenity_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE hotel_facility(
hotel_id INT,
amenity_id INT,
PRIMARY KEY (hotel_id, amenity_id),
FOREIGN KEY (hotel_id) REFERENCES Hotel(hotel_id)
ON DELETE CASCADE,
FOREIGN KEY(amenity_id) REFERENCES Amenity(amenity_id)
ON DELETE CASCADE
);

CREATE TABLE Payment(
payment_id INT AUTO_INCREMENT PRIMARY KEY,
booking_id INT,
amount DECIMAL(10,2) NOT NULL,
payment_date DATE,
payment_method VARCHAR(50),
payment_status ENUM('paid','pending','failed'),
FOREIGN KEY(booking_id) REFERENCES Booking(booking_id)
ON DELETE CASCADE
);