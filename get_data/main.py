
import requests 
from bs4 import BeautifulSoup


def get_dj_label(dj_container):
    try:
        return dj_container.find("span",  {"class": "font-normal text-sm md:text-md lowercase"}).text
    except:
        return

def get_dj_name(dj_container):
    dj_with_label = dj_container.find("span",  {"class": "font-bold"}).text
    label = get_dj_label(dj_container)
    if label:
        dj_wo_label = dj_with_label.replace(label, "")
        return (dj_wo_label, get_dj_label(dj_container))
    return (dj_with_label, None)

def extract_djs(floor):
    djs = floor.find_all("div", "running-order-set__info")
    dj_names = [get_dj_name(dj) for dj in djs]

    return dj_names


if __name__ == "__main__":
    url = "https://www.berghain.berlin/en/event/73053/"
    crawl_url = requests.get(url)
    soup = BeautifulSoup(crawl_url.content, "html.parser")
    
    first_floor = soup.find("div", {"data-set-floor":"1"})

    dj_names = extract_djs(first_floor)


    print(dj_names)
