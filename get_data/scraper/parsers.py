import itertools

import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


def remove_white_spaces(string):
    if string:
        return " ".join(string.split())
    return ""


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


class Set:

    def __init__(self, set_soup, floor_name):
        self.set_soup = set_soup
        self.floor_name = floor_name
        self.set_dict = self.bulid_set_dict()

    def get_label_and_set_type(self, dj_container):
        label = dj_container.find("span", {"class": "font-normal text-sm md:text-md lowercase"})
        set_type = dj_container.find("span", {"class": "text-sm md:text-md font-bold uppercase self-end text-white"})

        return label, set_type

    def parse_dj_container(self, set_soup):
        dj_soup = set_soup.find("div", class_="running-order-set__info")
        dj_name = dj_soup.find("span", class_="font-bold").text
        label, set_type = self.get_label_and_set_type(dj_soup)

        if label:
            dj_name = dj_name.replace(label.text, "")
        if set_type:
            dj_name = dj_name.replace(set_type.text, "")

        return dj_name, label, set_type

    def bulid_set_dict(self):
        set_dict = {}

        dj_name, label, set_type = self.parse_dj_container(self.set_soup)

        set_dict["dj_name"] = remove_white_spaces(dj_name)
        set_dict["label"] = remove_white_spaces(label.text) if label is not None else ""
        set_dict["set_type"] = remove_white_spaces(set_type.text) if set_type is not None else ""
        set_dict["starting_time"] = self.set_soup.get("data-set-item-start")
        set_dict["ending_time"] = self.set_soup.get("data-set-item-end")
        set_dict["floor"] = self.floor_name
        return set_dict


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
        return remove_white_spaces(event_name)

    def get_event_date(self, soup):

        date_container = soup.find("p", class_="text-sm md:text-md")
        date = date_container.find("span", class_="font-bold").text
        return remove_white_spaces(date)


    def get_sets_per_floor(self, floor):

        floor_name = remove_white_spaces(floor.find("h2").text)

        sets_soup = floor.find_all("li")
        sets = [Set(set_soup, floor_name).set_dict for set_soup in sets_soup]

        return sets

    def construct_sets_per_floor_dict(self, soup):
        floors = soup.find_all("div", {"class" : "mt-1/4"})
        sets = []

        for floor in floors:
            floor_sets = self.get_sets_per_floor(floor)
            sets.append(floor_sets)

        return list(itertools.chain.from_iterable(sets))

    def extract(self):

        event = {}
        soup = self.load_soup()
        event["event_name"] = self.get_event_name(soup)
        event["event_date"] = self.get_event_date(soup)
        event["sets"] = self.construct_sets_per_floor_dict(soup)

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
