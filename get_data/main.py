import json
import itertools
import pandas as pd

from parsers import EventPageParser, MonthPageParser

class Main:

    def __init__(self):

        self.base_archive_url = "https://www.berghain.berlin/en/program/archive/"
        self.base_event_url = "https://www.berghain.berlin"

    def _format_month(self, month):

        return str(month) if month > 9 else f"0{month}"

    def fetch_month_events(self, year, month):
        formated_month = self._format_month(month)
        url = f"{self.base_archive_url}{year}/{formated_month}/"

        events_extractor = MonthPageParser(url)
        event_ids = events_extractor.extract()

        events = []

        for id in event_ids:
            url = self.base_event_url + id
            timetable_extractor = EventPageParser(url)

            event = timetable_extractor.extract()
            events.append(event)

        return events

    def fetch_years_events(self, year):
        years_events = []
        for i in range(1, 13):
            try:
                years_events.append(self.fetch_month_events(year, i))
            except Exception as e:
                continue

        return list(itertools.chain.from_iterable(years_events))

    def convert_to_flatten_dataframe(self, events):

        flatten_df = pd.json_normalize(
            events, "sets", ["event_name", "event_date"]
        )
        return flatten_df




    def write_to_json(self, events):
        json_object = json.dumps(events)

        with open("sample.json", "w") as outfile:
            outfile.write(json_object)


if __name__ == "__main__":

    main = Main()

    #months_events = main.fetch_month_events(2016, 2)
    #print(months_events)
    years_events = main.fetch_years_events(2016)
    flatten_df = main.convert_to_flatten_dataframe(years_events)
    flatten_df.to_csv("berghain_2016_sets.csv", index=False)