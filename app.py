# import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database and tables
base = automap_base()
base.prepare(engine, reflect = True)

# Save reference to the tables
measurement = base.classes.measurement
station = base.classes.station
session = Session(engine)

# Find the most recent date in the data set.
most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()

# Calculate the date one year from the last date in data set.
date = dt.date(2017,8,23) - dt.timedelta(days = 365)
session.close()

# Create an app
app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Welcome to Hawaii Climate Page<br/> "
        f"All available Routes:<br/>"
        f"<br/>"  
        f"List of precipitation data with dates:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"List of stations and names:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"List of temprture observations from a year from the last data point:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Min, Max. and Avg. temperatures for given start date: (use 'yyyy-mm-dd' format):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"<br/>"
        f"Min. Max. and Avg. tempratures for given start and end date: (use 'yyyy-mm-dd'/'yyyy-mm-dd' format for start and end dates):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<br/>"
        f"i.e. <a href='/api/v1.0/min_max_avg/2012-01-01/2016-12-31' target='_blank'>/api/v1.0/min_max_avg/2012-01-01/2016-12-31</a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Returns the dictionary for date and precipitation info"""
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()
    precipitation = []
    for result in results:
        r = {}
        r[result[0]] = result[1]
        precipitation.append(r)
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a JSON list of stations from the dataset."""
    results = session.query(station.station, station.name).all()
    session.close()
    station_list = []
    for result in results:
        r = {}
        r["station"]= result[0]
        r["name"] = result[1]
        station_list.append(r)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    results = session.query(measurement.tobs, measurement.date).filter(measurement.date >= date).all()
    session.close()
    tobs_list = []
    for result in results:
        r = {}
        r["date"] = result[1]
        r["temprature"] = result[0]
        tobs_list.append(r)
    return jsonify(tobs_list)

@app.route("/api/v1.0/min_max_avg/<start>")
def start(start):
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date"""
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_dt).all()
    session.close()
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)
    return jsonify(t_list)

@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given end date."""
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_dt).filter(measurement.date <= end_dt)
    session.close()
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["EndDate"] = end_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)
    return jsonify(t_list)

#run the app
if __name__ == "__main__":
    app.run(debug=True)