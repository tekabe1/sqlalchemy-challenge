# Import the dependencies.
from flask import Flask, jsonify, g
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import datetime as dt

# Create an instance of Flask
app = Flask(__name__)

# Create an engine to connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session factory
Session = sessionmaker(bind=engine)


# Function to get or create a session
def get_session():
    if 'session' not in g:
        # Create a new session if it doesn't exist
        g.session = Session()
    return g.session


# Close the session at the end of each request
@app.teardown_appcontext
def teardown_session(exception=None):
    session = g.pop('session', None)
    if session is not None:
        session.close()


# Define the home route
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = get_session()

    # Calculate the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(
        most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)


# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    session = get_session()

    # Query the list of stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    stations_list = [station for station, in results]

    return jsonify(stations_list)


# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = get_session()

    # Calculate the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(
        most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the temperature observations for the most active station in the last 12 months
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago). \
        filter(Measurement.station == 'USC00519397').all()

    # Convert the query results to a list of dictionaries
    temperature_data = [{date: tobs} for date, tobs in results]

    return jsonify(temperature_data)


# Define the start date route
@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = get_session()

    # Query the minimum, average, and maximum temperature for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
        filter(Measurement.date >= start).all()

    # Convert the query results to a list of dictionaries
    temp_data = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax}
                 for tmin, tavg, tmax in results]

    return jsonify(temp_data)


# Define the start and end date route
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    session = get_session()

    # Query the minimum, average, and maximum temperature for dates between the start and end dates (inclusive)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the query results to a list of dictionaries
    temp_data = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax}
                 for tmin, tavg, tmax in results]

    return jsonify(temp_data)


if __name__ == "__main__":
    app.run(debug=True)
