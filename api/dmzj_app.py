import time
from urllib.parse import *

"""dmzj.com (app) lang=zh"""

__author__ = 'ssj'


def search(s, kw):
    page = 0
    results_lst = []
    kw = quote(quote(kw))  # url encode twice
    url = 'https://v3api.dmzj.com/search/show/0/' + kw + '/'
    while True:
        r = s.get(url + str(page) + '.json', timeout=180)  # request n=number_of_pages times
        if r.text == '[]':
            if page == 0:
                return -1
            else:
                break
        else:
            for comic_json in r.json():

                title = comic_json['title']
                auth = comic_json['authors']
                latest = comic_json['last_name']
                status = comic_json['status']
                href = 'https://v3api.dmzj.com/comic/' + str(comic_json['id']) + '.json'

                comic = \
                    {'title': title, 'auth': auth, 'href': href, 'latest': latest, 'status': status,
                     'module': module, 'site': site}

                results_lst.append(comic)
            page += 1
            time.sleep(0.2)
    return results_lst


def info(s, url):
    headers = {'referer': url}
    r = s.get(url, timeout=180)
    info_json = r.json()
    id = info_json['id']
    title = info_json['title']
    cover_url = info_json['cover']
    cover = s.get(cover_url, headers=headers, timeout=180).content
    auth = info_json['authors'][0]['tag_name']
    intro = info_json['description']
    status = info_json['status'][0]['tag_name']
    chaps = []
    for chap in info_json['chapters'][0]['data']:
        chaps.append(
            {
                'chap_title': chap['chapter_title'],
                'chap_href': 'https://v3api.dmzj.com/chapter/' + str(id) + '/' + str(chap['chapter_id']) + '.json'
            })

    latest = chaps[0]['chap_title']
    chaps.reverse()

    result = {'title': title,
              'cover': cover,
              'auth': auth,
              'chaps': chaps,
              'latest': latest,
              'status': status,
              'intro': intro,
              'module': module,
              'site': site}
    return result


def get_img_urls(s, url):
    r = s.get(url, timeout=180)
    dl_json = r.json()
    img_urls = dl_json['page_url']
    headers = {'User-Agent': 'Platform/304 CFNetwork/975.0.3 Darwin/18.2.0', 'Referer': 'http://imgsmall.dmzj.com/'}
    return [img_urls, headers]


module = "dmzj_app"
site = "动漫之家"
request_method = ""
