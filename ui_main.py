from comic_download.ui import *


class UIForm(QWidget):
    def __init__(self):
        super(UIForm, self).__init__()

        self.search_edit = QLineEdit(self)
        self.search_button = QPushButton(self)
        self.tabWidget = QTabWidget(self)
        self.search_tab = QWidget()
        self.dl_tab = QWidget()
        self.pause_dl_button = AllPauseButton(None)
        self.del_dl_button = QPushButton(None)

        self.tabWidget.tabCloseRequested.connect(self.tab_remove)

    def setup_ui(self):
        form_width = 800
        form_height = 600
        self.setGeometry(300, 100, form_width, form_height)
        self.setFixedSize(form_width, form_height)
        self.setWindowTitle("Comic Downloader")

        self.setObjectName("form")
        self.search_edit.setObjectName("search_edit")
        self.search_button.setObjectName("search_button")
        self.del_dl_button.setObjectName("del_dl_button")
        self.pause_dl_button.setObjectName("pause_dl_button")
        self.tabWidget.setObjectName("tabWidget")
        self.search_tab.setObjectName("search_tab")
        self.dl_tab.setObjectName("dl_tab")

        self.search_edit.setGeometry(13, 16, 700, 21)
        self.search_button.setGeometry(730, 12, 68, 32)
        self.tabWidget.setGeometry(12, 55, 780, 550)
        self.del_dl_button.setGeometry(668, 485, 100, 32)
        self.pause_dl_button.setGeometry(560, 485, 100, 32)

        self.search_button.setText("搜索")
        self.del_dl_button.setText("清空下载")
        self.pause_dl_button.setText("全部暂停")

        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(False)

        self.tabWidget.addTab(self.search_tab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.search_tab), "搜索结果")

        self.tabWidget.addTab(self.dl_tab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dl_tab), "下载任务")
        self.tabWidget.setCurrentIndex(0)
        self.del_dl_button.setParent(self.dl_tab)
        self.pause_dl_button.setParent(self.dl_tab)

        self.del_dl_button.hide()
        self.del_dl_button.setDisabled(True)

    def tab_remove(self, index):
        """close the tab"""

        if index != 0 and index != self.tabWidget.count() - 1:
            self.tabWidget.removeTab(index)
