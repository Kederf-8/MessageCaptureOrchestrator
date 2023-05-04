import re
import time

import requests
from bs4 import BeautifulSoup, Comment

REGEX_URL = (
    r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})"
    + "|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]"
    + "|[01]?[0-9][0-9]?))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}"
    + "|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"
)


def find_all_urls(text):
    """Returns an array of URLs found in the given text."""
    matches = re.findall(REGEX_URL, text)
    return matches


def ensure_protocol(url, protocol="https"):
    """Ensures that the URL has the specified protocol."""
    base = "http"
    if isinstance(url, str):
        if url[: len(base)] != base:
            url = f"{protocol}://{url}"
    if isinstance(url, list):
        for i in range(len(url)):
            if url[i][: len(base)] != base:
                url[i] = f"{protocol}://{url[i]}"
    return url


def tag_visible(element):
    """Helper function for text_from_html."""
    if element.parent.name in [
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    """Extracts visible text from the given HTML body."""
    soup = BeautifulSoup(body, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts)


def load_and_parse(address):
    """Loads the given URL and extracts visible text from its HTML body."""
    print(f"[LOAD AND PARSE] {address}")
    print(f"\nLoading {address} ...")
    time.sleep(0.01)
    try:
        response = requests.get(address, verify=False, timeout=7)
        if not response.ok:
            print(f"[ERRORE]: la pagina {address} non è stata caricata")
            return "null"
        return text_from_html(response.text)
    except Exception as e:
        print(f"(load_and_parse): {e}")
        return "null"


if __name__ == "__main__":
    example_input = """add1 http://mit.edu.com abc
        add2 https://unict.com . abc
        add3 www.google.be. uvw
        add4 https://www.google.it. 123
        add5 www.website.gov.us test2
        Hey bob on www.test.com.
        another test with ipv4 http://192.168.1.1/test.jpg. toto2
        website with different port number www.test.com:8080/test.jpg not port 80
        www.website.gov.uk/login.html
        test with ipv4 (192.168.1.1/test.jpg).
        search at lorenzo.tap.com/ukraine"""
    urls = find_all_urls(example_input)
    urls_with_protocol = ensure_protocol(urls)
