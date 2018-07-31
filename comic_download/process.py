import requests
import json
import multiprocessing as mp
import os
import asyncio
import aiohttp
import time
import zipfile


headers = {'Referer': 'http://imgsmall.dmzj.com/'}
global q1
global q2
q1 = mp.Queue()  # download queue
q2 = mp.Queue()  # update queue


def chap_info(all_tasks):
    """get the task from the queue and download it"""

    task = q1.get()
    task['state'] = 0
    all_tasks[task['index']] = task
    q2.put(task)
    path_init = os.path.abspath('.')
    if not os.path.exists('./download'):
        os.mkdir('download')
    os.chdir('./download')

    comic = task['comic'].replace('/', ' ')
    chap = task['chap'].replace('/', ' ')
    if not os.path.exists('./' + comic):
        os.mkdir(comic)
    os.chdir(comic)
    if not os.path.exists('./' + chap):
        os.mkdir(chap)
    os.chdir(chap)

    url = task['url']

    session = requests.Session()
    session.trust_env = False
    r = session.get(url)
    r_json = r.json()
    page_num = r_json['picnum']
    task['page_num'] = page_num
    page_urls = r_json['page_url']
    task['state'] = 1
    all_tasks[task['index']] = task
    q2.put(task)

    image_tasks = [image_dl(page_url, task, all_tasks) for page_url in page_urls]
    image_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(image_loop)
    image_loop.run_until_complete(asyncio.wait(image_tasks))

    if task['progress'] == page_num:
        os.chdir(os.path.dirname(os.path.abspath('.')))
        with zipfile.ZipFile(' '.join((comic, chap)) + '.zip', 'a') as zip_chap:
            for root, dirs, files in os.walk('./' + chap):
                for file in files:
                    zip_chap.write(root + '/' + file)
        task['state'] = 2
        all_tasks[task['index']] = task
        q2.put(task)

    os.chdir(path_init)


async def image_dl(url, task, all_tasks):
    """download images"""

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as get_image:
            filename = os.path.basename(url)
            image = await get_image.read()
            with open(filename, 'wb') as f:
                f.write(image)
            task['progress'] += 1
            all_tasks[task['index']] = task
            q2.put(task)
            time.sleep(0.1)


def task_upd():
    """detect and update"""

    task = q2.get()
    return task
