# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import statistics
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
base = automap_base()
base.prepare(autoload_with=engine)

# Save references to each table

measurement = base.classes.measurement
station = base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

# Start session
session = Session(engine)

# Find most recent date 
date_list = session.query(measurement.date)
recent_date = [x[0] for x in date_list]
recent_date = max(recent_date)
    
# Find date 12 months before
recent_date_clean = dt.datetime.strptime(recent_date, "%Y-%m-%d").date()
date_one_year = recent_date_clean - dt.timedelta(days=365)

# Retrieve station names
station_list = session.query(measurement.station)

station_names = []
    
for name in station_list:
    station_names.append(name)

station_names = set(station_names)
station_names = [x[0] for x in station_names]

# Find most active station
station_counts = []

for station in station_names:
    number_rows = session.query(measurement.station).filter(measurement.station == station).count()
    station_counts.append(number_rows)
    
active_stations_df = pd.DataFrame({"station": station_names,
                                   "number of rows": station_counts})
    
active_stations_df = active_stations_df.sort_values("number of rows",ascending=False)
active_stations_df = active_stations_df.reset_index(drop=True)

# Close session
session.close()


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    return (
        "Welcome, the available routes are the following <br/>"
        "/Resources/hawaii.sqlite <br/>"
        "/api/v1.0/stations <br/>"
        "/api/v1.0/tobs <br/>"
        "/api/v1.0/start-date (yyyy-mm-dd) <br/>"
        "/api/v1.0/start-date (yyyy-mm-dd)/end-date (yyyy-mm-dd)")

@app.route("/Resources/hawaii.sqlite")
def hawaii():
    # Start session
    session = Session(engine)

    # Query DB
    one_year_prec = session.query(measurement).filter(measurement.date >= date_one_year).filter(measurement.date <= recent_date_clean)

    # Save query results
    
    prpc_dict = [{"date": x.date,
                  "prcp": x.prcp} for x in one_year_prec]
    
    # Jsonify
    return jsonify(prpc_dict )
    
    # Close session
    session.close()


@app.route("/api/v1.0/stations")
def stations():
    # Jsonify
    return jsonify(station_names)
    

@app.route("/api/v1.0/tobs")
def tobs():
    # Start session
    session = Session(engine)
    
    # Query DB to retrieve last 12 months data
    last_12_months_tobs = session.query(measurement).filter(measurement.station == active_stations_df["station"][0]).filter(measurement.date >= date_one_year).filter(measurement.date <= recent_date_clean)

    # Save query results
    
    last_12_months = [{"date": x.date,
                  "tobs": x.tobs} for x in last_12_months_tobs]

    # Jsonify
    return jsonify(last_12_months)
    
    # Close session
    session.close()

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Start session
    session = Session(engine)

    # Query DB 
    temp_data = session.query(measurement.tobs).filter(measurement.date >= str(start))

    # Save query results
    temp_data_list = [x[0] for x in temp_data]

    # Calculate
    max_temp = max(temp_data_list)
    min_temp = min(temp_data_list)
    mean_temp = statistics.mean(temp_data_list)
    
    # Summarize data
    temp_data_dict = {"lowest value": min_temp,
                      "highest value": max_temp,
                      "average": mean_temp}
    
    # Jsonify
    return jsonify(temp_data_dict)

    # Close session
    session.close()


@app.route("/api/v1.0/<start>/<end>")
def end_date(start,end):
    # Start session
    session = Session(engine)

    # Query DB 
    temp_data = session.query(measurement.tobs).filter(measurement.date >= str(start)).filter(measurement.date <= str(end))

    # Save query results
    temp_data_list = [x[0] for x in temp_data]

    # Calculate
    max_temp = max(temp_data_list)
    min_temp = min(temp_data_list)
    mean_temp = statistics.mean(temp_data_list)
    
    # Summarize data
    temp_data_dict = {"lowest value": min_temp,
                      "highest value": max_temp,
                      "average": mean_temp}
    
    # Jsonify
    return jsonify(temp_data_dict)

    # Close session
    session.close()


if __name__ == "__main__":
    app.run(debug=True)
