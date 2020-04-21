import os
import csv
import psycopg2
from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

engine = create_engine('postgres://postgres:0417@localhost:5432/booking')
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index1.html")

@app.route('/book', methods=["POST"])
def book():
    
    name = request.form.get("name")
    origin = request.form.get("origin")
    destination = request.form.get("destination")
    schedule = request.form.get("schedule")
    ticket = request.form.get("ticket")
    
    if name is None:
        return render_template("error.html", message="Name not found.")

    flights = db.execute("INSERT INTO flights (name, origin, destination, schedule, ticket) VALUES (:name, :origin, :destination, :schedule, :ticket)",
                {"name" : name, "origin" : origin, "destination" : destination, "schedule" : schedule, "ticket": ticket})
    
    flight = db.execute("SELECT * FROM flights ORDER BY id DESC LIMIT 1").fetchone()
    db.commit()
    return render_template("success.html", flight = flight)


@app.route("/flights", methods = ["POST"])
def flights():

    f = open('flights.csv')
    reader = csv.reader(f)
    for origin, destination, duration in reader:
        db.execute("INSERT INTO available (origin, destination, duration) VALUES (:origin, :destination, :duration)",
                   {"origin": origin, "destination": destination, "duration": duration})
    #db.commit()

    """ Lists all flights """
    flights = db.execute("SELECT * FROM available").fetchall()
    return render_template("flights.html", flights=flights)

@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    """Lists details about a single Flight"""

    flight = db.execute("SELECT * FROM available WHERE id = :id", {"id" : flight_id}).fetchone()
    if flight is None:
        return render_template("error.html", message = "No such flight exists")
    return render_template("flight2.html", flight=flight)
if __name__ == "__main__":
    app.run()