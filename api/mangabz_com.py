from lxml.html import etree
import re
import execjs
import time

"""mangabz.com, lang=cn"""

__author__ = 'ssj'


def search(s, kw):
    url = 'https://www.mangabz.com/search?title=' + kw
    headers['referer'] = 'https://www.mangabz.com'
    r = s.get(url, headers=headers, timeout=180)
    tree = etree.HTML(r.text)
    titles = tree.xpath('//ul[@class="mh-list"]/li/div/div/h2/a/text()')
    hrefs = tree.xpath('//ul[@class="mh-list"]/li/div/div/h2/a/@href')
    latests = tree.xpath('//ul[@class="mh-list"]/li/div/div/p/a/text()')
    results_lst = []
    for i in range(len(titles)):
        results_lst.append({
            'title': titles[i],
            'href': 'https://www.mangabz.com' + hrefs[i],
            'latest': latests[i],
            'status': '',
            'auth': '',
            'module': module,
            'site': site
        })
    return results_lst


def info(s, url):
    headers['referer'] = url
    r = s.get(url, headers=headers, timeout=180)
    tree = etree.HTML(r.text)
    title = tree.xpath('//p[@class="detail-info-title"]/text()')[0].strip()
    cover = tree.xpath('//img[@class="detail-info-cover"]/@src')[0]
    auth = tree.xpath('//p[@class="detail-info-tip"]/span[1]/a/text()')[0]
    status = tree.xpath('//p[@class="detail-info-tip"]/span[2]/span/text()')[0]
    intro = tree.xpath('//p[@class="detail-info-content"]/text()')[0]
    intro2 = tree.xpath('//p[@class="detail-info-content"]/span/text()')
    if intro2 != []:
        intro = intro + intro2[0]
    latest = tree.xpath('//span[@class="s"]/span/a/text()')[0].strip()
    chaps = []
    chaps_titles = tree.xpath('//div[@id="chapterlistload"]/a/text()[1]')
    chaps_hrefs = tree.xpath('//div[@id="chapterlistload"]/a/@href')
    for i in range(len(chaps_titles)):
        chaps.append({'chap_title': chaps_titles[i].strip(), 'chap_href': 'https://www.mangabz.com' + chaps_hrefs[i]})
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
    page_no = 1
    url = url.rstrip('/')
    img_urls = []

    while True:
        page_url = url + '-p' + str(page_no) + '/'
        r = s.get(page_url, headers=headers, timeout=180)
        if r.status_code == 404:
            break
        cid = re.compile('var MANGABZ_CID=[^;]*;').findall(r.text)[0].lstrip('var MANGABZ_CID=').rstrip(';')
        _mid = re.compile('var MANGABZ_MID=[^;]*;').findall(r.text)[0].lstrip('var MANGABZ_MID=').rstrip(';')
        _dt = re.compile('var MANGABZ_VIEWSIGN_DT=[^;]*;').findall(r.text)[0].lstrip(
            'var MANGABZ_VIEWSIGN_DT="').rstrip('";')
        _sign = re.compile('var MANGABZ_VIEWSIGN=[^;]*;').findall(r.text)[0].lstrip('var MANGABZ_VIEWSIGN="').rstrip(
            '";')

        img_ajax_url = page_url + 'chapterimage.ashx'
        params = {
            'cid': cid,
            'page': page_no,
            'key': '',
            '_cid': cid,
            '_mid': _mid,
            '_dt': _dt,
            '_sign': _sign
        }
        ajax_r = s.get(img_ajax_url, headers=headers, params=params)
        if ajax_r.text == '':
            return -3
        img_url = execjs.eval(ajax_r.text)
        img_urls.append(img_url[0])
        page_no += 1
        time.sleep(0.5)

    return [img_urls, headers]


headers = {'user-agent': 'Mozilla/5.0 (Macintosh; '
                         'Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/69.0.3497.100 Safari/537.36',
           'referer': ''}

module = 'mangabz_com'
site = 'mangabz.com'
request_method = ''
