"""
File containing utility functions.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup

def extract_text_from_url(url: str) -> str:
    """
    Extracts text from a given url and returns it
    in a human-readable format.
    """
    # get the html content from the url
    html = urlopen(url).read()
    # parse the html using bs4
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract() 

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # drop blank lines and form the final extracted text
    text = '\n'.join(line for line in lines if line)
    return text