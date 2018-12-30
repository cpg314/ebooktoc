import utils
import requests
from pprint import pprint

def getMetadata(isbn):
    utils.log("Fetching metadata from ISBN")
    isbn = isbn.replace("-", "")
    r = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:{}".format(isbn))
    out = []
    for r in r.json()["items"]:
        r = r["volumeInfo"]
        book = {}
        for k in ["authors", "publisher", "title"]:
            book[k] = r[k]
        book["year"] = r["publishedDate"].split("-")[0]
        out.append(book)        
    return out
