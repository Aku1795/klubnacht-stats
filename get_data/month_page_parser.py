from parser import Parser

class MonthPageParser(Parser):

    def __init__(self, url) -> None:
        super().__init__(url)

    def extract(self):
        soup = self.load_soup()

        events = soup.find_all("a",
                               class_="upcoming-event block p-3/4 md:p-1 pb-2 bg-light-black hover:bg-light-black-flash bg-clip-padding border-b-2 border-transparent")
        links = [e.get('href') for e in events]

        return links

