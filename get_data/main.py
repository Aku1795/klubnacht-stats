
import requests 

from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

from requests.api import get


class Extractor(ABC):

    @abstractmethod
    def __init__(self, url) -> None:
        self.url = url
    

class TimeTableExtractor(Extractor):

    def __init__(self, url) -> None:
        super().__init__(url)
    
    def get_dj_label(self, dj_container):
        try:
            return dj_container.find("span",  {"class": "font-normal text-sm md:text-md lowercase"}).text
        except:
            return

    def get_dj_name(self, dj_container):
        dj_with_label = dj_container.find("span",  {"class": "font-bold"}).text
        label = self.get_dj_label(dj_container)
        if label:
            dj_wo_label = dj_with_label.replace(label, "")
            return (dj_wo_label, self.get_dj_label(dj_container))
        return (dj_with_label, None)

    def extract_djs(self, floor):
        djs = floor.find_all("div", "running-order-set__info")
        dj_names = [self.get_dj_name(dj) for dj in djs]

        return dj_names 
    
    def extract(self):
        crawl_url = requests.get(self.url)
        soup = BeautifulSoup(crawl_url.content, "html.parser")
    
        first_floor = soup.find("div", {"data-set-floor":"1"})
        first_floor = soup.find("div", {"data-set-floor":"1"})

        dj_names = self.extract_djs(first_floor)
        return dj_names

class NightExtractor(Extractor):

    def __init__(self, url) -> None:
        super().__init__(url)


if __name__ == "__main__":
    url = "https://www.berghain.berlin/en/event/73053/"
    timetable_extractor = TimeTableExtractor(url)

    dj_names = timetable_extractor.extract()
    print(dj_names)
