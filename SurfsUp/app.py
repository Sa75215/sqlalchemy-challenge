import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with = engine)

measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def homepage():
    """List all available api routes"""
    return (
        f"Available routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session from python to the DB
    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= '2016-08-23').order_by(measurement.date >= '2016-08-23').all()
    session.close()

    all_precipitation =[]
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)
    

@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)
    stations = session.query(station.station).distinct().all()
    session.close()

    all_stations = list(np.ravel(stations))
    return jsonify(all_stations=all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    previous_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_results = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= previous_date).all()
    session.close()
    
    all_tobs_list =[]
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs_list.append(tobs_dict)
    return jsonify(all_tobs_list)

@app.route("/api/v1.0/<start>")
def start_temp(start):
    session = Session(engine)
    temp_list = session.query(measurement.date, measurement.tobs).all()
    session.close()

    tobs_temp_list = []
    for date, tobs in temp_list:
        temp_dict = {}
        temp_dict[date] = tobs
        tobs_temp_list.append(temp_dict)
    for temp_dict[date] in temp_list:
        if temp_dict[date] == start:
            min_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).all()
            max_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).all()
            avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).all()
            #test to see if it works
            return jsonify(min_temp)


if __name__ == "__main__":
    app.run(debug=True)