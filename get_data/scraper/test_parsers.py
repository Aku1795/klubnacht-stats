import pytest
from bs4 import BeautifulSoup
from parsers import EventPageParser

# Sample soup object for testing

# Sample URL for testing
url = "http://www.example.com/event"

def test_get_event_name():
    # Test that the get_event_name method returns the correct event name from a given soup object
    soup = BeautifulSoup("<html><body><h1>Event Name</h1></body></html>", "html.parser")
    parser = EventPageParser(url)
    assert parser.get_event_name(soup) == "Event Name"

def test_get_event_date():
    # Test that the get_event_date method returns the correct event date from a given soup object
    soup = BeautifulSoup("<html><body><p class='text-sm md:text-md'><span class='font-bold'>Event Date</span></p></body></html>", "html.parser")
    parser = EventPageParser(url)
    assert parser.get_event_date(soup) == "Event Date"

def test_get_label_and_set_type():
    # Test that the get_label_and_set_type method returns the correct label and set type from a given dj_container object
    dj_container = BeautifulSoup("<div><span class='font-normal text-sm md:text-md lowercase'>Label</span><span class='text-sm md:text-md font-bold uppercase self-end text-white'>Set Type</span></div>", "html.parser")
    parser = EventPageParser(url)
    label, set_type = parser.get_label_and_set_type(dj_container)
    assert label.text == "Label"