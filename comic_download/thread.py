from PyQt5.QtCore import *
import requests
import multiprocessing as mp
import json
from comic_download.process import *
import time


class PutThread(QThread):
    """put the tasks to the download queue"""

    new = pyqtSignal(dict)

    def __init__(self, tasks, all_tasks):
        super(PutThread, self).__init__()
        self.all_tasks = all_tasks
        self.tasks = tasks
        self.tasks_checked = []

    def run(self):

        self.check_task()
        for task in self.tasks_checked:
            q1.put(task)

    def check_task(self):
        for task in self.tasks:
            if len(self.all_tasks) != 0:
                if self.exist_task(task) == 0:
                    self.add_task(task)

            else:
                # no existed tasks
                self.add_task(task)

    def exist_task(self, task):
        i = 0
        for task_exist in self.all_tasks:
            if (task['comic'] == task_exist['comic']) and (task['chap'] == task_exist['chap']):
                # a same task exists
                return 1
            else:
                i += 1

        if i == len(self.all_tasks):
            # no same task
            return 0

    def add_task(self, task):
        task['index'] = len(self.all_tasks)
        self.tasks_checked.append(task)
        self.all_tasks.append(task)
        self.new.emit(task)


class DLThread(QThread):
    """download tasks from the queue"""

    def __init__(self, all_tasks):
        super(DLThread, self).__init__()
        self.all_tasks = all_tasks
        self.dl_pool = mp.Pool(4)

    def run(self):
        while True:
            if q1.empty():
                time.sleep(5)
                continue
            else:
                # the queue is not empty
                self.dl_pool.apply_async(chap_info, (self.all_tasks,))
                time.sleep(0.2)
        self.dl_pool.close()
        self.dl_pool.join()


class UPDThread(QThread):
    """update the UI"""

    info = pyqtSignal(dict)

    def __init__(self):
        super(UPDThread, self).__init__()
        self.upd_pool = mp.Pool()

    def run(self):
        self.update()

    def update(self):
        while True:
            if q2.empty():
                time.sleep(0.1)
                continue
            else:
                upd = self.upd_pool.apply_async(task_upd, ).get()
                self.info.emit(upd)
                time.sleep(0.1)
        self.upd_pool.close()
        self.upd_pool.join()


class InitThread(QThread):
    """open the save file and get the tasks"""

    init = pyqtSignal()

    def __init__(self, all_tasks):
        super(InitThread, self).__init__()
        self.all_tasks = all_tasks

    def run(self):
        with open('comic.txt', 'a+') as sav:
            sav.seek(0)
            if len(sav.read()) == 0:
                self.init.emit()
            else:
                sav.seek(0)
                for task in sav.readlines():
                    task = json.loads(task.replace('\n', ''))
                    state = task['state']
                    if state == -1:
                        q1.put(task)
                    self.all_tasks.append(task)
                time.sleep(1)
                self.init.emit()


class SaveThread(QThread):
    """save the download list to the save file before closed"""

    def __init__(self, all_tasks):
        super(SaveThread, self).__init__()
        self.all_tasks = all_tasks

    def run(self):
        with open('comic.txt', 'w+') as sav:
            for task in self.all_tasks:
                sav.write(json.dumps(task) + '\n')
