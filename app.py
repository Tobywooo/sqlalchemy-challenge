# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session as ORM_Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
db_engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
ModelBase = automap_base()
# reflect the tables
ModelBase.prepare(autoload_with=db_engine)

# Save references to each table
StationTable = ModelBase.classes.station
MeasurementTable = ModelBase.classes.measurement

# Create our session (link) from Python to the DB
db_session = ORM_Session(db_engine)

#################################################
# Flask Setup
#################################################
web_app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# List available routes
@web_app.route("/")
def homepage():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

# Convert query and return JSON
@web_app.route("/api/v1.0/precipitation")
def precipitation_data():
    orm_session = ORM_Session(db_engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    previous_year_date = dt.date(query_date.year, query_date.month, query_date.day)

    query_results = orm_session.query(MeasurementTable.date, MeasurementTable.prcp).filter(MeasurementTable.date >= previous_year_date).order_by(MeasurementTable.date.desc()).all()

    precipitation_data = dict(query_results)

    return jsonify(precipitation_data)

# Return list of stations JSON
@web_app.route("/api/v1.0/stations")
def stations_list():
    orm_session = ORM_Session(db_engine)
    selection = [StationTable.station, StationTable.name, StationTable.latitude, StationTable.longitude, StationTable.elevation]
    station_query_result = orm_session.query(*selection).all()
    orm_session.close()

    station_list = []
    for station, name, lat, lon, elevation in station_query_result:
        station_info = {"Station": station, "Name": name, "Latitude": lat, "Longitude": lon, "Elevation": elevation}
        station_list.append(station_info)

    return jsonify(station_list)

# Query dates and temperatures for the previous year of data from the most active station and return JSON list
@web_app.route("/api/v1.0/tobs")
def temperature_observations():
    orm_session = ORM_Session(db_engine)

    temp_query_result = orm_session.query(MeasurementTable.date, MeasurementTable.tobs).filter(MeasurementTable.station == 'USC00519281')\
    .filter(MeasurementTable.date >= '2016-08-23').all()

    temperature_data = []
    for date, temp in temp_query_result:
        temp_record = {"Date": date, "Temperature": temp}
        temperature_data.append(temp_record)

    return jsonify(temperature_data)

# Return JSON list of minimum temperature, average temperature, and max temperature for a given start date
@web_app.route("/api/v1.0/<start>")
def get_temperatures_from_start(start):
    orm_session = ORM_Session(db_engine)
    temp_results = orm_session.query(func.min(MeasurementTable.tobs), func.avg(MeasurementTable.tobs), func.max(MeasurementTable.tobs))\
                  .filter(MeasurementTable.date >= start).all()
    orm_session.close()

    temp_ranges = []
    for min_temp, avg_temp, max_temp in temp_results:
        temp_info = {'Minimum Temperature': min_temp, 'Average Temperature': avg_avg_temp, 'Maximum Temperature': max_temp}
        temp_ranges.append(temp_info)

    return jsonify(temp_ranges)

# Return JSON list of min temp, avg temp, and max temp for a given start and end date
@web_app.route("/api/v1.0/<start>/<end>")
def get_temperatures_from_range(start, end):
    orm_session = ORM_Session(db_engine)
    temp_results = orm_session.query(func.min(MeasurementTable.tobs), func.avg(MeasurementTable.tobs), func.max(MeasurementTable.tobs))\
                  .filter(MeasurementTable.date >= start).filter(MeasurementTable.date <= end).all()
    orm_session.close()

    temp_ranges = []
