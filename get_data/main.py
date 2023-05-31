import pandas as pd
import os

from parsers import EventPageParser, MonthPageParser
from utils import write_dataframe_to_gcs
from flask import request, Flask

BASE_ARCHIVE_URL = "https://www.berghain.berlin/en/program/archive/"
BASE_EVENT_URL = "https://www.berghain.berlin"
BUCKET = "klubnacht-stats-raw-10101"

## utils

def _format_month(month):
    return str(month) if month > 9 else f"0{month}"

def fetch_month_events(base_archive_url, base_event_url,year, month):
    formated_month = _format_month(month)
    url = f"{base_archive_url}{year}/{formated_month}/"

    events_extractor = MonthPageParser(url)
    event_ids = events_extractor.extract()

    events = []

    for id in event_ids:

        url =f"{base_event_url}{id}"
        timetable_extractor = EventPageParser(url)

        event = timetable_extractor.extract()
        events.append(event)

    return events

def convert_to_flatten_dataframe(events):

    flatten_df = pd.json_normalize(
        events, "sets", ["event_name", "event_date"]
    )
    return flatten_df

#app
app = Flask(__name__)

# Routes
@app.route("/")
def index():
    return "Let's crap baby"

@app.route("/scrap_month", methods=["POST"])
def scrap_month():

    data = request.json
    year = data["year"]
    month = int(data["month"])

    events = fetch_month_events(BASE_ARCHIVE_URL, BASE_EVENT_URL, year, month)
    flatten_df = convert_to_flatten_dataframe(events)
    write_dataframe_to_gcs(flatten_df, BUCKET, f"berghain_{year}_{_format_month(month)}_sets.csv")

    return f"Scrapped {year}-{month} events"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

