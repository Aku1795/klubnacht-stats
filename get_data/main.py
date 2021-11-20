
import requests 
from bs4 import BeautifulSoup

def extract_djs(floor):
    djs = floor.find_all("div", "running-order-set__info")
    dj_names = [dj.find("span").text for dj in djs]

    return dj_names


if __name__ == "__main__":
    url = "https://www.berghain.berlin/en/event/73053/"
    crawl_url = requests.get(url)
    soup = BeautifulSoup(crawl_url.content, "html.parser")
    
    first_floor = soup.find("div", {"data-set-floor":"0"})

    dj_names = extract_djs(first_floor)


    print(dj_names)
