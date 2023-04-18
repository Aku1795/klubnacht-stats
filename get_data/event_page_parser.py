from parser import Parser

class EventPageParser(Parser):

    def __init__(self, url) -> None:
        super().__init__(url)
    

    def get_event_name(self, soup):

        event_name = soup.find("h1").text
        return self.remove_white_spaces(event_name)
    
    def get_event_date(self, soup):

        date_container = soup.find("p", class_ = "text-sm md:text-md")
        date = date_container.find("span", class_ = "font-bold").text
        return self.remove_white_spaces(date)
    
    def get_floors(self, soup):
        floors = []
        for i in range(5):
            floor = soup.find("div", {"data-set-floor":f"{i}"})
            if floor:
                floors.append(floor)
        return floors

    def get_dj_label(self, dj_container):
        try:
            return dj_container.find("span",  {"class": "font-normal text-sm md:text-md lowercase"}).text
        except:
            return
    
    def get_dj_name_and_label(self, set_soup):
        dj_soup = set_soup.find("div",  class_ = "running-order-set__info")
        dj_string = dj_soup.find("span",  class_ = "font-bold").text
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

        #rint(soup)
        floors = self.get_floors(soup)
        event["event_name"] = self.get_event_name(soup)
        event["event_date"] = self.get_event_date(soup)
        event["sets_per_floor"] = self.construct_sets_per_floor_dict(floors)

        return event


if __name__ == "__main__":
    url = "https://www.berghain.berlin/en/event/73053/"
    timetable_extractor = EventPageParser(url)

    dj_names = timetable_extractor.extract()
    print(dj_names)



