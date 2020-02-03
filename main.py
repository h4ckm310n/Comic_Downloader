from ui_main import UIForm
from comic_search.ui import *
from comic_search.thread import SearchThread
from comic_info.ui import *
from comic_info.thread import InfoThread
from comic_download.ui import *
from comic_download.thread import *
from comic_download.process import *
from multiprocessing.managers import BaseManager
import cfscrape
import requests


class Manager(BaseManager):
    def __init__(self):
        super(Manager, self).__init__()
        self.manager = mp.Manager()
        self.register("CloudflareScraper", cfscrape.CloudflareScraper)
        self.register("Session", requests.Session)
        self.all_tasks = self.manager.dict()
        self.pool_pid = self.manager.dict()
        self.start()


class Main(UIForm):
    def __init__(self):
        super(Main, self).__init__()
        self.setup_ui()

        # initialize the download list
        self.all_tasks = all_tasks
        self.task_index = task_index
        self.cfs = cfs
        self.rs = rs
        self.init_dialog = InitDialog(self)
        self.dl_list = DLList(self.dl_tab)
        self.dl_frames = {}
        self.init_thread = InitThread(self.all_tasks, self.task_index)
        self.init_thread.init.connect(self.dl_init)

        # save the download list to the save file before closed
        self.save_thread = SaveThread(self.all_tasks)

        # infinite looped threads to detect the queues respectively
        self.task_thread = TaskThread(self.all_tasks, self.task_index, self.cfs, self.rs, pool_pid)
        self.upd_thread = UPDThread()
        self.upd_thread.info.connect(self.dl_update)

        self.init_thread.start()
        self.init_dialog.exec_()

        self.task_thread.start()
        self.upd_thread.start()

        self.search_thread = None
        self.pause_thread = None
        self.info_thread = None
        self.put_thread = None

        self.search_dialog = None

        self.info_tab = None
        self.info_dialog = None

        self.search_button.clicked.connect(self.start_search)
        self.pause_dl_button.clicked.connect(self.pause_all)
        self.del_dl_button.clicked.connect(self.del_all)

    def closeEvent(self, a0):
        """save the download list to the save file before closed"""

        self.task_thread.quit()
        self.save_thread.start()

    def dl_init(self):
        """initialize the download list"""

        if len(self.all_tasks) != 0:
            for i in range(len(self.all_tasks)):
                self.add_task(self.all_tasks[i])
        self.dl_list.show()
        self.init_dialog.closable = 1
        self.init_dialog.close()

    def start_search(self):
        """search"""

        text = self.search_edit.text()
        if text != '':
            self.search_dialog = SearchDialog(self)

            self.search_thread = SearchThread(text, self.cfs, self.rs)

            self.search_thread.state.connect(self.search_state)
            self.search_thread.result.connect(self.search_list)

            self.search_thread.start()

    def search_state(self, state):
        search_state(self.search_dialog, state)

    def search_list(self, results):
        """list the results"""

        result_list = ResultList(self.search_tab)

        for result in results:
            result_list.add_to_list(result)

        result_list.show()
        self.tabWidget.setCurrentIndex(0)

    def comic_clicked(self, href, module):
        """the title label of a search result is clicked"""

        self.info_dialog = InfoDialog(self)
        self.info_thread = InfoThread(href, module, self.cfs, self.rs)
        self.info_thread.info_state.connect(self.info_state)
        self.info_thread.info.connect(self.comic_info)
        self.info_thread.start()

    def info_state(self, state):
        info_state(self.info_dialog, state)

    def comic_info(self, info):
        """show the info of the clicked comic in a new tab"""

        self.info_tab = QWidget()
        self.info_tab.setObjectName('info_tab')
        self.tabWidget.insertTab(1, self.info_tab, '')
        self.tabWidget.setCurrentIndex(1)
        info_frame = InfoFrame(info, self.info_tab)
        info_frame.show()

    def download_clicked(self, comic, checkboxes):
        """the download button is clicked"""

        tasks = []
        for checked in checkboxes:
            chap = checked.chap
            url = checked.url
            module = checked.module
            tasks.append(
                {"module": module, "comic": comic, "index": 0, "chap": chap, "url": url,
                 "progress": 0, "page_num": 1, "state": dl_state_dict['waiting']})
        self.put_thread = PutThread(tasks, self.all_tasks, self.task_index)
        self.put_thread.new.connect(self.add_task)
        self.put_thread.start()
        self.tabWidget.setCurrentWidget(self.dl_tab)

    def add_task(self, task):
        """add a new task in the UI"""

        frame = ItemFrame(task, self.dl_list)
        self.dl_list.add_to_list(frame)
        self.dl_frames[task['index']] = frame

    def dl_update(self, task):
        """update the download list"""

        i = task['index']
        progress = task['progress']
        page_num = task['page_num']
        state = task['state']

        frame = self.dl_frames[i]
        if frame.state != state:
            frame.state_change(state)
        frame.progress_update(page_num, progress)

    def pause_dl(self, index):
        """pause task"""

        if self.task_thread.end_flag == 1:
            return
        self.pause_thread = PauseThread(index, pool_pid)
        self.pause_thread.start()

    def resume_dl(self, index):
        """resume task"""

        q1.put(self.all_tasks[index])
        if self.task_thread.end_flag == 1:
            self.task_thread.end_flag = 0
            self.task_thread.start()

    def del_task(self, index):
        """delete task"""

        del self.all_tasks[index]
        del self.dl_frames[index]

    def pause_all(self):
        """pause all tasks"""

        if self.pause_dl_button.flag == 1:
            self.resume_all()
            return
        self.put_thread.terminate()
        self.task_thread.end_flag = 1
        for frame in self.dl_frames.values():
            if frame.state == dl_state_dict['analyzing'] or frame.state == dl_state_dict['downloading']:
                frame.pause_label.state_change()
        self.pause_dl_button.flag_change(1)

    def resume_all(self):
        """resume all tasks"""

        for frame in self.dl_frames.values():
            if frame.state == dl_state_dict['pause']:
                frame.pause_label.state_change()
        self.task_thread.end_flag = 0
        self.task_thread.start()
        self.pause_dl_button.flag_change(0)

    def del_all(self):
        """delete all tasks"""

        frames = []
        for frame in self.dl_frames.values():
            if frame.state == dl_state_dict['waiting'] or frame.state == dl_state_dict['finished']:
                frames.append(frame)

        for frame in frames:
            frame.del_task()


if __name__ == "__main__":
    import sys
    manager = Manager()
    app = QApplication(sys.argv)
    rs = manager.Session()
    cfs = manager.CloudflareScraper()
    all_tasks = manager.all_tasks
    pool_pid = manager.pool_pid
    task_index = mp.Value("i", 0)
    main = Main()
    main.show()
    sys.exit(app.exec_())
