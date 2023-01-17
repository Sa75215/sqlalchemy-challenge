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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
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

#dynamic route. if ony start date given, end date default is none.
@app.route('/api/v1.0/<start>', defaults = {'end':None})
@app.route("/api/v1.0/<start>/<end>")
def temps_for_date_range(start, end):
#Open session and do if statement where if end date is given, temp data calculated filters incorporate end dates to get range. if no end date given, temp calculations only use start date.
    session = Session(engine)
    if end != None:
        min_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        max_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        
    else:
        min_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).all()
        max_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).all()
        avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    
    session.close()
    
    
    #capture variables
    print("min_temp output:", min_temp)
    print("max_temp output:", max_temp)
    print("avg_temp output:", avg_temp)

#     #go in to the variable and extract just the temps needed. current format is single tuple with single value and comma
    min_temp = min_temp[0][0]
    max_temp = max_temp[0][0]
    avg_temp = avg_temp[0][0]

    results = {
        "Min temp": min_temp,
        "Max temp": max_temp,
        "Average temp": avg_temp
     }
#             #test to see if it works
    
#     # print(jsonify(results))
#if any of the data is missing below, the date range chosen doesn't have data needed and new date range should be chosen
    if min_temp == None or max_temp == None or avg_temp == None:
        return f"No temperature data found for the given date range. Try another date range."
    else:
        return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)