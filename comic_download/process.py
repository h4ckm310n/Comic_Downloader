import multiprocessing as mp
import os
import signal
from PIL import Image
import asyncio
import aiohttp
import time
import zipfile
import importlib
from comic_download import dl_state_dict


global q1
global q2
q1 = mp.Queue()  # download queue
q2 = mp.Queue()  # update queue


def dl_worker(all_tasks, cfs, rs, pool_pid):
    """get the task from the queue and download it"""

    print('proc start')

    task = q1.get()
    if not task['index'] in all_tasks:
        return 0

    task['state'] = dl_state_dict['analyzing']
    pid = os.getpid()
    index = task['index']
    pool_pid[index] = pid
    all_tasks[task['index']] = task
    q2.put(task)

    url = task['url']
    module = importlib.import_module('.' + task['module'], 'api')
    if module.request_method == "cfs":
        time.sleep(5)
        r = module.get_img_urls(cfs, url)
    else:
        r = module.get_img_urls(rs, url)
    if r == -3:
        task['state'] = -3
        all_tasks[task['index']] = task
        return -3

    img_urls = r[0]
    headers = r[1]
    page_num = len(img_urls)
    task['page_num'] = page_num
    task['state'] = dl_state_dict['downloading']
    all_tasks[task['index']] = task
    q2.put(task)
    dl_proc(task, img_urls, headers, all_tasks, page_num)
    del pool_pid[index]
    del all_tasks[task['index']]['pid']
    return 0


def dl_proc(task, img_urls, headers, all_tasks, page_num):
    # directory
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
    task['progress'] = 0

    image_tasks = [image_dl(i, img_urls, headers, task, all_tasks) for i in range(len(img_urls))]
    image_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(image_loop)
    image_loop.run_until_complete(asyncio.wait(image_tasks))

    if task['progress'] == page_num:
        # cbz
        os.chdir(os.path.dirname(os.path.abspath('.')))
        with zipfile.ZipFile(' '.join((comic, chap)) + '.cbz', 'w') as zip_chap:
            for root, dirs, files in os.walk('./' + chap):
                for file in files:
                    zip_chap.write(root + '/' + file)

        # pdf
        img_files = []
        images = []
        for root, dirs, files in os.walk('./' + chap):
            for file in files:
                img_files.append([root, os.path.splitext(file)[0], os.path.splitext(file)[-1]])
        img_files = sorted(img_files, key=lambda k: int(k[1]))
        for imgf in img_files:
            image_temp = Image.open(imgf[0] + '/' + imgf[1] + imgf[2])
            images.append(image_temp.convert('RGB'))
        images[0].save(' '.join((comic, chap)) + '.pdf', save_all=True, append_images=images[1:])

        task['state'] = dl_state_dict['finished']
        all_tasks[task['index']] = task
        q2.put(task)

    os.chdir(path_init)


async def image_dl(i, urls, headers, task, all_tasks):
    """download images"""

    async with aiohttp.ClientSession() as session:
        async with session.get(urls[i], headers=headers) as get_image:
            filename = str(i) + '.jpg'
            print('download ' + task['chap'] + ' ' + task['chap'] + ' ' + filename)
            image = await get_image.read()
            with open(filename, 'wb') as f:
                f.write(image)
            task['progress'] += 1
            all_tasks[task['index']] = task
            q2.put(task)
            time.sleep(0.3)


def task_upd():
    """detect and update"""

    task = q2.get()
    return task
