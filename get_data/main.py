import json

from event_page_parser import EventPageParser
from month_page_parser import MonthPageParser

if __name__ == "__main__":
    # url = "https://www.berghain.berlin/en/event/73053/"
    # timetable_extractor = TimeTableExtractor(url)

    # dj_names = timetable_extractor.extract()
    # print(dj_names)

    base_path = "https://www.berghain.berlin"

    url = "https://www.berghain.berlin/en/program/archive/2019/12/"
    events_extractor = MonthPageParser(url)
    links = events_extractor.extract()
    events =[]
    for link in links:
        url = base_path + link
        timetable_extractor = EventPageParser(url)

        event = timetable_extractor.extract()
        events.append(event)


    json_object = json.dumps(events)

    with open("sample.json", "w") as outfile:
        outfile.write(json_object)

