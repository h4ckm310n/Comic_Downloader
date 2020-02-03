from lxml.html import etree

"""readcomiconline.ru, lang=en"""

__author__ = 'ssj'


def search(s, kw):
    results_lst = []
    url = 'https://readcomicsonline.ru/search?query=' + kw
    r = s.get(url, headers=headers, timeout=180)
    for comic in r.json()['suggestions']:
        title = comic['value']
        href = 'https://readcomicsonline.ru/comic/' + comic['data']
        results_lst.append(
            {'title': title, 'auth': '', 'href': href, 'latest': '', 'status': '', 'module': module, 'site': site})
    return results_lst


def info(s, url):
    headers['referer'] = 'https://readcomicsonline.ru'
    r = s.get(url, headers=headers, timeout=180)
    tree = etree.HTML(r.text)
    title = tree.xpath('//img[@class="img-responsive"]/@alt')[0]
    cover = 'https:' + tree.xpath('//img[@class="img-responsive"]/@src')[0]
    auth = tree.xpath('//dl[@class="dl-horizontal"]/dd[1]/text()')[0].strip()
    status = tree.xpath('//dl[@class="dl-horizontal"]/dd[2]/span/text()')[0].strip()
    if status == 'Ongoing':
        status = '连载中'
    else:
        status = '已完结'
    intro = tree.xpath('//div[@class="manga well"]/p/text()')[0]
    chaps = []
    chaps_titles = tree.xpath('//h5[@class="chapter-title-rtl"]/a/text()')
    chaps_hrefs = tree.xpath('//h5[@class="chapter-title-rtl"]/a/@href')
    for i in range(len(chaps_titles)):
        chaps.append({'chap_title': chaps_titles[i], 'chap_href': chaps_hrefs[i]})
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
    headers['referer'] = url
    r = s.get(url, headers=headers, timeout=180)
    tree = etree.HTML(r.text)
    img_urls = tree.xpath('//div[@id="all"]/img/@data-src')
    for i in range(len(img_urls)):
        img_urls[i] = img_urls[i].strip()
    return [img_urls, headers]


headers = {'user-agent': 'Mozilla/5.0 (Macintosh; '
                         'Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/69.0.3497.100 Safari/537.36',
           'referer': ''}

module = 'readcomicsonline_ru'
site = 'readcomicsonline.ru'
request_method = ''
