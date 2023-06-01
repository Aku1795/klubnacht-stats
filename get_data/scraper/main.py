import pandas as pd
import os

from parsers import EventPageParser, MonthPageParser
from utils import write_dataframe_to_gcs, format_month, compute_last_year_month
from flask import request, Flask

BASE_ARCHIVE_URL = "https://www.berghain.berlin/en/program/archive/"
BASE_EVENT_URL = "https://www.berghain.berlin"
BUCKET = os.getenv("BUCKET")


## scrapping methods

def fetch_month_events(base_archive_url, base_event_url, year, month):
    url = f"{base_archive_url}{year}/{month}/"

    events_extractor = MonthPageParser(url)
    event_ids = events_extractor.extract()

    events = []

    for id in event_ids:
        url = f"{base_event_url}{id}"
        timetable_extractor = EventPageParser(url)

        event = timetable_extractor.extract()
        events.append(event)

    return events


def convert_to_flatten_dataframe(events):
    flatten_df = pd.json_normalize(
        events, "sets", ["event_name", "event_date"]
    )
    return flatten_df

def scrap_and_upload_events(year, month):
    events = fetch_month_events(BASE_ARCHIVE_URL, BASE_EVENT_URL, year, month)
    flatten_df = convert_to_flatten_dataframe(events)
    write_dataframe_to_gcs(flatten_df, BUCKET, f"berghain_{year}_{month}_sets.csv")

    return f"Scraped {year}-{month} events"



# app
app = Flask(__name__)


# Routes
@app.route("/")
def index():
    return "Let's scrap baby"


@app.route('/scrap_last_month', methods=['GET'])
def scrap_last_month():
    year, month = compute_last_year_month()
    month = format_month(month)

    return scrap_and_upload_events(year, month)


@app.route("/scrap_month", methods=["POST"])
def scrap_month():
    data = request.json
    year = data["year"]
    month = format_month(int(data["month"]))

    return scrap_and_upload_events(year, month)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
