import requests
import cfscrape
from lxml.html import etree
import time
import json


def comic_modules():
    with open('config.json', 'r') as file:
        modules_dict = json.load(file)
    return modules_dict
