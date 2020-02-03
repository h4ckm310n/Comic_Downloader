from PyQt5.QtCore import *
import json
from comic_download.process import *
import time
import comic_download


class PutThread(QThread):
    """put the tasks to the download queue"""

    new = pyqtSignal(dict)

    def __init__(self, tasks, all_tasks, task_index):
        super(PutThread, self).__init__()
        self.all_tasks = all_tasks
        self.tasks = tasks
        self.task_index = task_index
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
        for task_exist in self.all_tasks.values():
            if (task['comic'] == task_exist['comic']) and (task['chap'] == task_exist['chap']):
                # a same task exists
                return 1
            else:
                i += 1

        if i == len(self.all_tasks):
            # no same task
            return 0

    def add_task(self, task):
        task['index'] = self.task_index.value
        self.tasks_checked.append(task)
        self.all_tasks[self.task_index.value] = task
        self.task_index.value += 1
        self.new.emit(task)


class TaskThread(QThread):
    """download tasks from the queue"""

    def __init__(self, all_tasks, task_index, cfs, rs, pool_pid):
        super(TaskThread, self).__init__()
        self.all_tasks = all_tasks
        self.task_index = task_index
        self.cfs = cfs
        self.rs = rs
        self.pool_pid = pool_pid
        self.end_flag = 0
        self.pool = None

    def run(self):
        self.pool = mp.Pool(comic_download.get_max_process())
        while True:
            '''if len(self.pool) == 4:
                time.sleep(5)
                continue'''
            if self.end_flag == 1:
                self.pool.terminate()
                while not q1.empty():
                    q1.get()
                return
            if q1.empty():
                time.sleep(5)
                continue
            else:
                # the queue is not empty
                self.pool.apply_async(dl_worker, (self.all_tasks, self.cfs, self.rs, self.pool_pid,))
                time.sleep(2)


class PauseThread(QThread):
    def __init__(self, index, pool_pid):
        super(PauseThread, self).__init__()
        self.index = index
        self.pool_pid = pool_pid

    def run(self):
        print('         pause ' + str(self.index) + ' ' + str(self.pool_pid[self.index]))

        try:
            os.kill(self.pool_pid[self.index], signal.SIGTERM)
            del self.pool_pid[self.index]
        except ProcessLookupError:
            return


class ResumeThread(QThread):
    def __init__(self, index, all_tasks):
        super(ResumeThread, self).__init__()
        self.index = index
        self.all_tasks = all_tasks

    def run(self):
        q1.put(self.all_tasks[self.index])


class UPDThread(QThread):
    """update the UI"""

    info = pyqtSignal(dict)

    def __init__(self):
        super(UPDThread, self).__init__()
        self.upd_pool = mp.Pool(comic_download.get_max_process())

    def run(self):
        self.update()

    def update(self):
        while True:
            if q2.empty():
                time.sleep(0.1)
                continue
            else:
                upd = self.upd_pool.apply_async(task_upd,).get()
                self.info.emit(upd)
                time.sleep(0.1)
        self.upd_pool.close()
        self.upd_pool.join()


class InitThread(QThread):
    """open the save file and get the tasks"""

    init = pyqtSignal()

    def __init__(self, all_tasks, task_index):
        super(InitThread, self).__init__()
        self.all_tasks = all_tasks
        self.task_index = task_index

    def run(self):
        with open('comic.log', 'a+') as sav:
            sav.seek(0)
            if len(sav.read()) == 0:
                self.init.emit()
            else:
                sav.seek(0)
                for task in sav.readlines():
                    task = json.loads(task.replace('\n', ''))
                    task['index'] = self.task_index.value
                    if task['state'] != dl_state_dict['finished']:
                        q1.put(task)
                    self.all_tasks[self.task_index.value] = task
                    self.task_index.value += 1
                time.sleep(1)
                self.init.emit()


class SaveThread(QThread):
    """save the download list to the save file before closed"""

    def __init__(self, all_tasks):
        super(SaveThread, self).__init__()
        self.all_tasks = all_tasks

    def run(self):
        while not q2.empty():
            continue
        with open('comic.log', 'w+') as sav:
            for task in self.all_tasks.values():
                sav.write(json.dumps(task) + '\n')
