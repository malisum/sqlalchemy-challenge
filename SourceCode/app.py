###======================================================================================================================================================###
# # Directory structure:
###======================================================================================================================================================###

# /sqlalchemy-challenge/Resources: Resources used by script, like Database etc.

# /sqlalchemy-challenge/SourceCode for Source code
#    # app.py: Script for Flask
#    # climate.ipynb: Script to read DB and produce output 

# /sqlalchemy-challenge/Output: Output maps/images produced by the script

# /sqlalchemy-challenge/Instructions: Instructions and materials provided as part of the exercise 

###======================================================================================================================================================###


###======================================================================================================================================================###
# Import Dependencies
###======================================================================================================================================================###

# Import Dependencies
import numpy as np
import pandas as pd
import datetime as dt
import flask
from flask import jsonify, Flask

# Reflect Tables into SQLAlchemy ORM
# Import - Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, alias, and_

###======================================================================================================================================================###


###======================================================================================================================================================###
# Precipitation
###======================================================================================================================================================###
# Query to retrieve the last 12 months of precipitation 

def q_precipitation():

    # Connection syntax for sqlite://<nohostname>/<path> where <path> is relative: So in this case use .. to go one folder up
    engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
    # Reflect an existing database into a new model
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    # Save references to each table
    Measurement = Base.classes.measurement
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    maxdate_str = session.query(func.max(Measurement.date)).first()[0]
    # Convert to date (use dt.datetime.strptime().date())
    maxdate = dt.datetime.strptime(maxdate_str, '%Y-%m-%d').date()
    maxdate_1yearago = maxdate - dt.timedelta(days=365)
    maxdate_1yearago_str = maxdate_1yearago.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    # Dropped where precipitation is NULL (can be done in Pandas Datframe also)
    precip_scores_result = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= maxdate_1yearago_str).filter(Measurement.prcp.isnot(None)).all()
    
    # Close the connection & Return 
    session.close()
    return precip_scores_result


###======================================================================================================================================================###
# Stations
###======================================================================================================================================================###
# Query to retrieve the stations

def q_stations():

    # Connection syntax for sqlite://<nohostname>/<path> where <path> is relative: So in this case use .. to go one folder up
    engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
    # Reflect an existing database into a new model
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    # Save references to each table
    Station = Base.classes.station
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the stations data 
    stations_result = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Close the connection & Return 
    session.close()
    return stations_result


###======================================================================================================================================================###
# Tobs
###======================================================================================================================================================###
# Query to retrieve the last 12 months of tobs

def q_tobs():

    # Connection syntax for sqlite://<nohostname>/<path> where <path> is relative: So in this case use .. to go one folder up
    engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
    # Reflect an existing database into a new model
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    # Save references to each table
    Measurement = Base.classes.measurement
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    maxdate_str = session.query(func.max(Measurement.date)).first()[0]
    # Convert to date (use dt.datetime.strptime().date())
    maxdate = dt.datetime.strptime(maxdate_str, '%Y-%m-%d').date()
    maxdate_1yearago = maxdate - dt.timedelta(days=365)
    maxdate_1yearago_str = maxdate_1yearago.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data 
    tobsscores_result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= maxdate_1yearago_str).all()
    
    # Close the connection & Return 
    session.close()
    return tobsscores_result


###======================================================================================================================================================###
# By Date
###======================================================================================================================================================###
# Query to retrieve by start date (and end date if provided)

def q_byDate(sdate, edate=None):

    # Connection syntax for sqlite://<nohostname>/<path> where <path> is relative: So in this case use .. to go one folder up
    engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
    # Reflect an existing database into a new model
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    # Save references to each table
    Measurement = Base.classes.measurement
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # If not end date: (start only), calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    if edate == None:
        startdate = dt.datetime.strptime(sdate, '%Y%m%d').strftime('%Y-%m-%d')
        searchdate_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
            .filter(Measurement.date>=startdate)\
            .group_by(Measurement.date).all()

    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    else:
        startdate = dt.datetime.strptime(sdate, '%Y%m%d').strftime('%Y-%m-%d')
        enddate = dt.datetime.strptime(edate, '%Y%m%d').strftime('%Y-%m-%d')
        searchdate_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
            .filter(Measurement.date>=startdate).filter(Measurement.date<=enddate)\
            .group_by(Measurement.date).all()

    # Close the connection & Return
    session.close()
    return searchdate_result


###======================================================================================================================================================###

# Main app code for API:

###======================================================================================================================================================###


# Flask Setup:
app = Flask(__name__)


# Flask Routes:

###=============================###
### Home / Welcome 
### "/" 
###=============================###

@app.route("/")
def welcome():
    return (
        f"Welcome to the wetaher station API!<br/>"
        f"Available APIs:"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation"
        f"<br/>"
        f"/api/v1.0//api/v1.0/stations"
        f"<br/>"
        f"/api/v1.0/tobs"
        f"<br/>"
        f"/api/v1.0/<start> OR /api/v1.0/<start>/<end>"
        f"<br/>"
    )

###=============================###
### Precipitation Results (JSON - Date & Precipitation)
### "/api/v1.0/precipitation"
###=============================###

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Fetch the precipitation data, or a 404 if not found."""

    # Use the function defined above to get the answer 
    p_rseult = q_precipitation()
    if p_rseult == None:
        return jsonify({"error": f"Not found."}), 404
    else:
        return jsonify(p_rseult)

###=============================###
### Stations Results (JSON)
### "/api/v1.0/stations"
###=============================###

@app.route("/api/v1.0/stations")
def stations():
    """Fetch the stations data, or a 404 if not found."""

    # Use the function defined above to get the answer 
    s_rseult = q_stations()
    if s_rseult == None:
        return jsonify({"error": f"Not found."}), 404
    else:
        return jsonify(s_rseult)

###=============================###
### Temperature Results (JSON)
### "/api/v1.0/tobs"
###=============================###

@app.route("/api/v1.0/tobs")
def tobs():
    """Fetch the temperature data, or a 404 if not found."""

    # Use the function defined above to get the answer 
    t_rseult = q_tobs()
    if t_rseult == None:
        return jsonify({"error": f"Not found."}), 404
    else:
        return jsonify(t_rseult)

###=============================###
### Temperature Results (JSON)
### "/api/v1.0/<start>"
###=============================###

@app.route("/api/v1.0/<start>")
def by_sdate(start):
    """Fetch the temperature based on date """
    
    td_rseult = q_byDate(start)
    if td_rseult == None:
        return jsonify({"error": f"Not found."}), 404
    else:
        return jsonify(td_rseult)

###=============================###
### Temperature Results (JSON)
### "/api/v1.0/<start>/<end>"
###=============================###

@app.route("/api/v1.0/<start>/<end>")
def by_date(start,end):
    """Fetch the temperature based on date """
    
    td_rseult = q_byDate(start, end)
    if td_rseult == None:
        return jsonify({"error": f"Not found."}), 404
    else:
        return jsonify(td_rseult)
    
###=============================###
### Main
###=============================###

if __name__ == "__main__":
    app.run(debug=True)

