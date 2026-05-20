DROP DATABASE IF EXISTS smart_travel;
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

CREATE TABLE Favourite (
    favourite_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    hotel_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (hotel_id) REFERENCES Hotel(hotel_id) ON DELETE CASCADE
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


USE smart_travel;

INSERT INTO Users (name, email, password, role) VALUES
('Anas Malik','anas@gmail.com','1234','traveler'),
('Sara Khan','sara@gmail.com','1234','traveler'),
('Ali Raza','ali@gmail.com','1234','admin');

INSERT INTO Hotel (name, city, address, price_per_night, rating, owner_id) VALUES
('Pearl Continental','Lahore','Mall Road',20000,4.5,3),
('Avari Hotel','Lahore','Shahrah-e-Quaid-e-Azam',18000,4.2,3),
('Serena Hotel','Islamabad','Sector G-5',25000,4.7,3),
('Luxus Grand','Lahore','Egerton Road',15000,4.3,3),
('Hunza Resort','Hunza','Karimabad',12000,4.6,3),
('Skardu Palace','Skardu','Near Airport Road',14000,4.4,3);

INSERT INTO Room (hotel_id, room_type, price, availability_status) VALUES
(1,'Single',8000,TRUE),
(1,'Double',12000,TRUE),
(2,'Single',7000,TRUE),
(2,'Deluxe',11000,TRUE),
(3,'Suite',20000,TRUE),
(3,'Double',15000,TRUE),
(4,'Single',6000,TRUE),
(4,'Double',10000,TRUE),
(5,'Deluxe',9000,TRUE),
(5,'Suite',13000,TRUE),
(6,'Single',7500,TRUE),
(6,'Deluxe',12000,TRUE);

INSERT INTO Destination (name, city, description, travel_tips) VALUES
('Hunza Valley','Hunza','Famous for mountains and scenic beauty','Best time: May to September'),
('Skardu Valley','Skardu','Lakes, mountains and cold desert','Carry warm clothes'),
('Murree Hills','Murree','Popular hill station near Islamabad','Avoid weekends due to rush'),
('Fairy Meadows','Gilgit','View of Nanga Parbat','Requires jeep ride'),
('Swat Valley','Swat','Switzerland of Pakistan','Visit in spring for greenery');

INSERT INTO Attraction (destination_id, name, description, location) VALUES
(1,'Attabad Lake','Beautiful blue lake','Hunza'),
(1,'Baltit Fort','Historic fort','Karimabad'),
(2,'Shangrila Resort','Heaven on earth','Skardu'),
(3,'Mall Road','Shopping street','Murree'),
(4,'Nanga Parbat View','Mountain viewpoint','Fairy Meadows'),
(5,'Malam Jabba','Ski resort','Swat');

INSERT INTO Review (user_id, hotel_id, rating, comment, review_date) VALUES
(1,1,5,'Amazing stay and great service!',CURDATE()),
(2,1,4,'Very comfortable rooms',CURDATE()),
(1,2,4,'Nice location but a bit expensive',CURDATE()),
(2,3,5,'Luxury experience!',CURDATE()),
(1,5,5,'Beautiful scenery and peaceful',CURDATE());

INSERT INTO Amenity (amenity_name) VALUES
('WiFi'),
('Swimming Pool'),
('Parking'),
('Gym'),
('Restaurant'),
('Room Service');
INSERT INTO hotel_facility VALUES
(1,1),(1,2),(1,5),
(2,1),(2,3),
(3,1),(3,2),(3,4),(3,5),
(4,1),(4,6),
(5,1),(5,3),(5,5),
(6,1),(6,4);