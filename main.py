from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui_main import UIForm
from comic_search.ui import *
from comic_search.thread import SearchThread
from comic_info.ui import *
from comic_info.thread import InfoThread
from comic_download.ui import *
from comic_download.thread import *
from comic_download.process import *


class Main(UIForm):
    def __init__(self, all_tasks):
        super(Main, self).__init__()

        # initialize the download list
        self.all_tasks = all_tasks
        self.init_dialog = InitDialog(self)
        self.dl_list = DLList(self.dl_tab)
        self.dl_frames = []
        self.init_thread = InitThread(self.all_tasks)
        self.init_thread.init.connect(self.dl_init)
        self.init_thread.start()
        self.init_dialog.exec_()

        # save the download list to the save file before closed
        self.save_thread = SaveThread(self.all_tasks)
        # self.save_thread.saved.connect(self.close)

        # infinite looped threads to detect the queues respectively
        self.dl_thread = DLThread(self.all_tasks)
        self.upd_thread = UPDThread()
        self.upd_thread.info.connect(self.dl_update)
        self.dl_thread.start()
        self.upd_thread.start()

        self.search_thread = None
        self.info_thread = None
        self.put_thread = None

        self.search_dialog = None

        self.info_tab = None
        self.info_dialog = None

        self.setup_ui()

        self.search_button.clicked.connect(self.start_search)

    def closeEvent(self, a0):
        """save the download list to the save file before closed"""

        self.save_thread.start()

    def dl_init(self):
        """initialize the download list"""

        if len(self.all_tasks) != 0:
            for i in range(len(self.all_tasks)):
                self.all_tasks[i]['index'] = i
                self.add_task(self.all_tasks[i])
        self.dl_list.show()
        self.init_dialog.closable = 1
        self.init_dialog.close()

    def start_search(self):
        """search"""

        text = self.search_edit.text()
        if text != '':
            self.search_dialog = SearchDialog(self)

            self.search_thread = SearchThread(text)

            self.search_thread.state.connect(self.search_state)
            self.search_thread.result.connect(self.search_list)

            self.search_thread.start()

    def search_state(self, state):
        search_state(self.search_dialog, state)

    def search_list(self, results):
        """list the results"""

        result_list = ResultList(self.search_tab)

        for result in results:
            title = result['title']
            auth = result['auth']
            latest = result['latest']
            status = result['status']
            id = result['id']

            result_list.add_to_list(title, auth, latest, status, id)

        result_list.show()
        self.tabWidget.setCurrentIndex(0)

    def comic_clicked(self, title, auth, latest, status, id):
        """the title label of a search result is clicked"""

        self.info_dialog = InfoDialog(self)
        self.info_thread = InfoThread(title, auth, latest, status, id)
        self.info_thread.info_state.connect(self.info_state)
        self.info_thread.info.connect(self.comic_info)
        self.info_thread.start()

    def info_state(self, state):
        info_state(self.info_dialog, state)

    def comic_info(self, info):
        """show the info of the clicked comic in a new tab"""

        title = info['title']
        cover = info['cover']
        auth = info['auth']
        latest = info['latest']
        status = info['status']
        intro = info['intro']
        chaps = info['chaps']
        id = info['id']

        self.info_tab = QWidget()
        self.tabWidget.insertTab(1, self.info_tab, '')
        self.tabWidget.setTabText(1, title)
        self.tabWidget.setCurrentIndex(1)
        info_frame = InfoFrame(title, cover, auth, latest, status, intro, chaps, id, self.info_tab)
        info_frame.show()

    def download_clicked(self, comic, checkboxes):
        """the download button is clicked"""

        tasks = []
        for checked in checkboxes:
            chap = checked.chap
            url = checked.url
            tasks.append(
                {"comic": comic, "index": 0, "chap": chap, "url": url, "progress": 0, "page_num": 1, "state": -1})
        self.put_thread = PutThread(tasks, self.all_tasks)
        self.put_thread.new.connect(self.add_task)
        self.put_thread.start()
        self.tabWidget.setCurrentWidget(self.dl_tab)

    def add_task(self, task):
        """add a new task in the UI"""

        title = task['comic']
        chap = task['chap']
        page_num = task['page_num']
        state = task['state']
        progress = task['progress']
        frame = ItemFrame(title, chap, page_num, progress, state, self.dl_list)
        self.dl_list.add_to_list(frame)
        self.dl_frames.append(frame)

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


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    manager = mp.Manager()
    all_tasks = manager.list()
    main = Main(all_tasks)
    main.show()
    sys.exit(app.exec_())
