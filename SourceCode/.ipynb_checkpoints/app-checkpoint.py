# Directory structure:

# /sqlalchemy-challenge/Resources: Resources used by script, like Database etc.

# /sqlalchemy-challenge/SourceCode for Source code
#    # app.py: Script for Flask
#    # climate.ipynb: Script to read DB and produce output 

# /sqlalchemy-challenge/Output: Output maps/images produced by the script

# /sqlalchemy-challenge/Instructions: Instructions and materials provided as part of the exercise 

# Import Dependencies

%matplotlib notebook
%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

# Import Dependencies

import numpy as np
import pandas as pd
import datetime as dt

# Reflect Tables into SQLAlchemy ORM

# Import - Python SQL toolkit and Object Relational Mapper

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, alias, and_

# SQL Engine 
# Connection syntax for sqlite://<nohostname>/<path> where <path> is relative: So in this case use .. to go one folder up

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Reflect an existing database into a new model

Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found

Base.classes.keys()

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Exploratory Climate Analysis

# Design a query to retrieve the last 12 months of precipitation data and plot the results

# Calculate the date 1 year ago from the last data point in the database
maxdate_str = session.query(func.max(Measurement.date)).first()[0]
# Convert to date (use dt.datetime.strptime().date())
maxdate = dt.datetime.strptime(maxdate_str, '%Y-%m-%d').date()
maxdate_1yearago = maxdate - dt.timedelta(days=365)
maxdate_1yearago_str = maxdate_1yearago.strftime('%Y-%m-%d')

# Perform a query to retrieve the data and precipitation scores
# Dropped where precipitation is NULL (can be done in Pandas Datframe also)
precip_scores = session.query(Measurement).filter(Measurement.date >= maxdate_1yearago_str).filter(Measurement.prcp.isnot(None)).all()

# Save the query results as a Pandas DataFrame and set the index to the date column
precip_scores_df = pd.read_sql(session.query(Measurement).filter(Measurement.date >= maxdate_1yearago_str).filter(Measurement.prcp.isnot(None)).statement, session.bind)
precip_scores_df.drop(columns=['id', 'station', 'tobs'], inplace=True)
precip_scores_df.rename(columns={"date": "Date", "prcp": "Precipitation"}, inplace=True)
precip_scores_df.set_index('Date')

# Sort the datafrme by date
precip_scores_df.sort_values(by=['Date'], inplace=True)

# Use Pandas Plotting with Matplotlib to plot the data
    
ax = precip_scores_df.plot.bar(x = 'Date', y='Precipitation', width = 40)
ax.axes.get_xaxis().set_visible(False)
plt.tight_layout()
plt.savefig("../Output/precipitation.png")
plt.show()

# Use Pandas to calcualte the summary statistics for the precipitation data

precip_scores_df.describe()

# Design a query to show how many stations are available in this dataset?

station_count = session.query(Station.station).group_by(Station.station).count()
print(station_count)

# What are the most active stations? (i.e. what stations have the most rows)?
# List the stations and the counts in descending order.

session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature of the most active station?

session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281').all()


# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram

# Extract the data
tobs_df = pd.read_sql(session.query(Measurement)\
                      .filter(Measurement.station == 'USC00519281')\
                      .filter(Measurement.date >= maxdate_1yearago_str)\
                      .statement, session.bind)

# PLot the histogram and add labels etc.
ax = tobs_df.hist(column = 'tobs', bins=11)
plt.legend(("tobs","tobs"))
plt.ylabel("Frequency", FontSize=10)
plt.title("")
plt.savefig("../Output/station-histogram.png")
plt.show()

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))

# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.

lowdate = (dt.datetime.strptime('2018-01-01', '%Y-%m-%d').date() - dt.timedelta(days=365)).strftime('%Y-%m-%d')
highdate = (dt.datetime.strptime('2018-01-07', '%Y-%m-%d').date() - dt.timedelta(days=365)).strftime('%Y-%m-%d')

calcdata = calc_temps(lowdate, highdate)
print(calcdata)

# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)

mintemp = calcdata[0][0]
avgtemp = calcdata[0][1]
maxtemp = calcdata[0][2]

plt.bar(x=1,height=avgtemp, yerr=(maxtemp-mintemp), color="peachpuff", width=0.75)
plt.xticks([])
plt.yticks([0,20,40,60,80,100])
plt.xlim(0,2)
plt.title("Trip Avg Temp")
plt.ylabel("Temp F")
plt.tight_layout()
plt.savefig("../Output/temperature.png")
plt.show()

# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation

session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation, func.coalesce(func.avg(Measurement.prcp),0))\
    .outerjoin(Measurement, and_(Station.station == Measurement.station, Measurement.date >= '2017-01-01', Measurement.date <= '2017-01-07'))\
    .group_by(Station.station)\
    .order_by(func.avg(Measurement.prcp).desc())\
    .all()

## Optional Challenge Assignment

# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
daily_normals("01-01")

# calculate the daily normals for your trip
# push each tuple of calculations into a list called `normals`

normals = []

# Set the start and end date of the trip
startdate = dt.datetime.strptime('2018-01-01', '%Y-%m-%d').date()
enddate = dt.datetime.strptime('2018-01-07', '%Y-%m-%d').date()

# Use the start and end date to create a range of dates
# Stip off the year and save a list of %m-%d strings
numdays = 7
datelist = []
mmddlist = []
for x in range (0, numdays):
    d = startdate + dt.timedelta(days = x)
    md = d.strftime('%m-%d')
    datelist.append(d)
    mmddlist.append(md)

# Loop through the list of %m-%d strings and calculate the normals for each date
for mmdd in mmddlist:
    normals.append(daily_normals(mmdd)[0])
    
print(normals)

# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index

# date range is datelist
normalsdf = pd.DataFrame(normals, columns =['Min', 'Avg', 'Max']) 
normalsdf['date'] = datelist
normalsdf.set_index('date', inplace=True)
normalsdf

# Plot the daily normals as an area plot with `stacked=False`
normalsdf.plot(kind='area', stacked=False)
xlocs=np.arange(len(datelist))
xlabs=[d.strftime('%Y-%m-%d') for d in datelist]
# plt.xticks(xlocs,xlabs)
plt.xticks(rotation=45)
plt.show()



# Import dependencies
from flask import Flask, jsonify

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the wetaher station API!<br/>"
        f"Available APIs:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0//api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation:
    """Fetch the precipitation data, or a 404 if not found."""

    for character in justice_league_members:
        search_term = character["real_name"].replace(" ", "").lower()

        if search_term == canonicalized:
            return jsonify(character)

    return jsonify({"error": f"Character with real_name {real_name} not found."}), 404


@app.route("/api/v1.0/justice-league/real_name/<real_name>")
def justice_league_by_real_name(real_name):
    """Fetch the Justice League character whose real_name matches
       the path variable supplied by the user, or a 404 if not."""

    canonicalized = real_name.replace(" ", "").lower()
    for character in justice_league_members:
        search_term = character["real_name"].replace(" ", "").lower()

        if search_term == canonicalized:
            return jsonify(character)

    return jsonify({"error": f"Character with real_name {real_name} not found."}), 404


@app.route("/api/v1.0/justice-league/superhero/<superhero>")
def justice_league_by_superhero__name(superhero):
    """Fetch the Justice League character whose superhero matches
       the path variable supplied by the user, or a 404 if not."""

    canonicalized = superhero.replace(" ", "").lower()
    for character in justice_league_members:
        search_term = character["superhero"].replace(" ", "").lower()

        if search_term == canonicalized:
            return jsonify(character)

    return jsonify({"error": "Character not found."}), 404


if __name__ == "__main__":
    app.run(debug=True)
