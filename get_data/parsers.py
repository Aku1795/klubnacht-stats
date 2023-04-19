import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class Parser(ABC):
    """
     An abstract class representing a parser for web pages.

    Attributes:
    -----------
    url: str
        The URL of the event page to be parsed.
    """

    @abstractmethod
    def __init__(self, url):
        self.url = url

    def load_soup(self):
        crawl_url = requests.get(self.url)
        return BeautifulSoup(crawl_url.content, "html.parser")

    def remove_white_spaces(self, string):
        if string:
            return " ".join(string.split())
        return ""

class EventPageParser(Parser):
    """
     A class used to parse an event page on Berghain website and extract information about the event.

    Attributes:
    -----------
    url: str
        The URL of the event page to be parsed.
    """

    def __init__(self, url) -> None:
        super().__init__(url)

    def get_event_name(self, soup):

        event_name = soup.find("h1").text
        return self.remove_white_spaces(event_name)

    def get_event_date(self, soup):

        date_container = soup.find("p", class_="text-sm md:text-md")
        date = date_container.find("span", class_="font-bold").text
        return self.remove_white_spaces(date)

    def get_floors(self, soup):
        floors = []
        for i in range(5):
            floor = soup.find("div", {"data-set-floor": f"{i}"})
            if floor:
                floors.append(floor)
        return floors

    def get_dj_label(self, dj_container):
        try:
            return dj_container.find("span", {"class": "font-normal text-sm md:text-md lowercase"}).text
        except:
            return

    def get_dj_name_and_label(self, set_soup):
        dj_soup = set_soup.find("div", class_="running-order-set__info")
        dj_string = dj_soup.find("span", class_="font-bold").text
        label = self.get_dj_label(dj_soup)
        if label:
            dj_name = dj_string.replace(label, "")
        else:
            dj_name = dj_string

        return dj_name, label

    def parse_set(self, set_soup):
        set = {}

        dj_name, label = self.get_dj_name_and_label(set_soup)

        set["dj_name"] = self.remove_white_spaces(dj_name)
        set["label"] = self.remove_white_spaces(label)
        set["starting_time"] = set_soup.get("data-set-item-start")
        set["ending_time"] = set_soup.get("data-set-item-end")
        return set

    def get_sets_per_floor(self, floor):

        floor_name = self.remove_white_spaces(floor.find("h2").text)

        sets_soup = floor.find_all("li")
        sets = [self.parse_set(set_soup) for set_soup in sets_soup]

        return floor_name, sets

    def construct_sets_per_floor_dict(self, floors):
        sets_per_floor = {}

        if len(floors) > 0:
            for floor in floors:
                floor_name, dj_names = self.get_sets_per_floor(floor)
                sets_per_floor[floor_name] = dj_names

        return sets_per_floor

    def extract(self):

        event = {}
        soup = self.load_soup()

        # rint(soup)
        floors = self.get_floors(soup)
        event["event_name"] = self.get_event_name(soup)
        event["event_date"] = self.get_event_date(soup)
        event["sets_per_floor"] = self.construct_sets_per_floor_dict(floors)

        return event

class MonthPageParser(Parser):

    def __init__(self, url) -> None:
        super().__init__(url)

    def extract(self):
        soup = self.load_soup()

        events = soup.find_all("a",
                               class_="upcoming-event block p-3/4 md:p-1 pb-2 bg-light-black hover:bg-light-black-flash bg-clip-padding border-b-2 border-transparent")
        links = [e.get('href') for e in events]

        return links

