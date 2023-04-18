import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class Parser(ABC):
    """
    An abstract class representing a parser for web pages.

    :param url: The URL of the page to be parsed.
    """

    @abstractmethod
    def __init__(self, url):
        self.url = url

    def load_soup(self):
        """
        Retrieve the HTML content of the page and parse it using BeautifulSoup.

        :return: A BeautifulSoup object representing the parsed content of the web page.
        """
        crawl_url = requests.get(self.url)
        return BeautifulSoup(crawl_url.content, "html.parser")

    def remove_white_spaces(self, string):
        """
        Remove any unnecessary white spaces from a given string.

        :param string: The string to be processed.
        :return: The processed string with unnecessary white spaces removed.
        """
        if string:
            return " ".join(string.split())
        return ""