from io import BytesIO
import re

from bs4 import BeautifulSoup
from PIL import Image
import requests


BASE_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=%s"


class ItemNotFoundError(Exception):
    pass


class WorkshopItem:
    def __init__(self, _id):
        self.id = str(_id)
        try:
            response = requests.get(BASE_URL % self.id)
        except requests.exceptions.ConnectionError:
            raise ItemNotFoundError
        html = response.text
        self.soup = BeautifulSoup(html, "lxml")
        elem = self.soup.find("div", class_="workshopItemTitle")
        if elem is None:
            raise ItemNotFoundError
        self.title = elem.text

    def get_img(self):
        javascript = self.soup.find("img", class_="workshopItemPreviewImageEnlargeable").parent["onclick"]
        pattern = re.compile(r"ShowEnlargedImagePreview\(\s*'(?P<url>.+)'\s*\);")
        img_url = pattern.match(javascript)["url"]
        response = requests.get(img_url)
        im = Image.open(BytesIO(response.content))
        return im


if __name__ == "__main__":
    test_id = "uihrgi"
    ws = WorkshopItem(test_id)
    print(ws.title)
    im = ws.get_img()
    im.show()
