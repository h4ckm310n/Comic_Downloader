from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


def info_state(info_dialog, state):
    if state == 3:
        info_dialog.closable = 2
        info_dialog.close()

    if state == 0:
        info_dialog.exec_()


class InfoDialog(QDialog):
    def __init__(self, parent):
        super(InfoDialog, self).__init__(parent)

        self.setObjectName("InfoDialog")
        self.setFixedSize(231, 120)
        self.setWindowTitle("正在获取信息")
        self.activateWindow()

        self.closable = 0

        self.label = QLabel(self)
        self.label.setGeometry(30, 20, 171, 21)
        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(130, 80, 81, 32)

        self.label.setText("正在获取漫画信息，请稍等……")
        self.pushButton.setText("取消")

        self.pushButton.clicked.connect(self.cancel)

    def cancel(self):
        self.closable = 1
        self.close()

    def closeEvent(self, a0):
        if self.closable == 0:
            a0.ignore()
        elif self.closable == 1:
            self.closable = 0
            self.parent().info_thread.terminate()
        elif self.closable == 2:
            self.closable = 0


class InfoFrame(QFrame):
    def __init__(self, title, cover, auth, latest, status, intro, chaps, id, parent):
        super(InfoFrame, self).__init__(parent)
        self.setObjectName('InfoFrame')
        self.setGeometry(20, 12, 740, 494)
        self.setFrameShape(QFrame.WinPanel)
        self.setFrameShadow(QFrame.Raised)

        self.title = title
        self.cover = cover
        self.auth = auth
        self.latest = latest
        self.status = status
        self.intro = intro
        self.chaps = chaps
        self.id = id
        self.chaps_titles = []
        self.urls = []

        for chap in self.chaps:
            self.chaps_titles.append(chap['chapter_title'])
            self.urls.append('http://v2api.dmzj.com/chapter/' + str(self.id) + '/' + str(chap['chapter_id']) + '.json')

        self.title_label = QLabel(self)
        self.cover_label = CoverLabel(self.cover, self)
        self.info_table = InfoTable(self)
        self.intro_scroll = QScrollArea(self)
        self.intro_label = QLabel(self.intro, self)
        self.big_list = List(self)
        self.checkboxes = []
        self.all_check = AllCheck(self)
        self.button = DLButton(self)
        self.set_widgets()

    def set_widgets(self):
        self.title_label.setGeometry(270, 20, 431, 21)
        text = '<html><head/><body><p><span style=" font-size:18pt; font-weight:600; color:#0000ff;">'\
            + self.title + '</span></p></body></html>'
        self.title_label.setText(text)
        self.intro_scroll.setGeometry(30, 340, 211, 131)
        self.intro_label.setGeometry(0, 0, 209, 129)
        self.intro_label.setFixedWidth(209)
        self.intro_label.setWordWrap(True)
        self.intro_scroll.setWidget(self.intro_label)
        self.intro_label.adjustSize()

        self.info_table.set_info(self.auth, self.latest, self.status, self.intro)
        rows = 19
        for i in range(0, len(self.chaps), rows):
            item_list = ItemList(self)
            if len(self.chaps) - i < rows:
                rows = len(self.chaps) - i
            for j in range(0, rows):
                checkbox = ChapCheck(i + j, self.chaps_titles[i + j], self.urls[i + j], self)
                self.checkboxes.append(checkbox)
                item_list.add_to_list(checkbox)
            self.big_list.add_list(item_list)
        self.button.setGeometry(612, 455, 81, 32)


class CoverLabel(QLabel):
    def __init__(self, cover, parent):
        super(CoverLabel, self).__init__(parent)
        self.cover = cover
        self.setGeometry(40, 20, 151, 210)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameShape(QFrame.Box)
        self.show_cover()

    def show_cover(self):
        image = QImage()
        image.loadFromData(self.cover)
        self.setPixmap(QPixmap(image).scaledToWidth(151))


class InfoTable(QTableWidget):
    def __init__(self, parent):
        super(InfoTable, self).__init__(3, 2, parent)
        self.setGeometry(30, 240, 211, 92)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

    def set_info(self, auth, latest, state, intro):
        auth_item = QTableWidgetItem('作者')
        auth_info = QTableWidgetItem(auth)
        latest_item = QTableWidgetItem('最新')
        latest_info = QTableWidgetItem(latest)
        state_item = QTableWidgetItem('状态')
        state_info = QTableWidgetItem(state)
        intro_item = QTableWidgetItem('简介')
        intro_info = QTableWidgetItem(intro)

        self.setItem(0, 0, auth_item)
        self.setItem(0, 1, auth_info)
        self.setItem(1, 0, latest_item)
        self.setItem(1, 1, latest_info)
        self.setItem(2, 0, state_item)
        self.setItem(2, 1, state_info)
        self.setItem(3, 0, intro_item)
        self.setItem(3, 1, intro_info)
        self.setColumnWidth(0, 70)
        self.setColumnWidth(1, 139)


class List(QListWidget):
    def __init__(self, parent):
        super(List, self).__init__(parent)
        self.setGeometry(270, 50, 431, 401)
        self.setFlow(QListView.LeftToRight)

    def add_list(self, item_list):
        item = QListWidgetItem(self)
        item.setSizeHint(QSize(171, 399))
        self.addItem(item)
        self.setItemWidget(item, item_list)


class ItemList(QListWidget):
    def __init__(self, parent):
        super(ItemList, self).__init__(parent)
        self.setObjectName('ItemList')
        self.setFixedSize(171, 399)

    def add_to_list(self, checkbox):
        item = QListWidgetItem(self)
        item.setSizeHint(QSize(161, 20))
        self.addItem(item)
        self.setItemWidget(item, checkbox)


class ChapCheck(QCheckBox):
    def __init__(self, i, chap, url, parent):
        super(ChapCheck, self).__init__(chap, parent)
        self.chap = chap
        self.url = url
        self.setObjectName('Chapcheck_' + str(i))
        self.setFixedSize(161, 20)


class AllCheck(QCheckBox):
    def __init__(self, parent):
        super(AllCheck, self).__init__('全选', parent)
        self.setGeometry(270, 460, 87, 20)
        self.checkboxes = self.parent().checkboxes
        self.stateChanged.connect(self.all_check)

    def all_check(self):
        if self.isChecked():
            for i in range(len(self.checkboxes)):
                self.checkboxes[i].setChecked(True)
        else:
            for i in range(len(self.checkboxes)):
                self.checkboxes[i].setChecked(False)


class DLButton(QPushButton):
    def __init__(self, parent):
        super(DLButton, self).__init__('下载', parent)
        self.checkboxes = self.parent().checkboxes
        self.title = self.parent().title
        self.clicked.connect(self.download)

    def download(self):
        checked = []
        for i in range(len(self.checkboxes)):
            if self.checkboxes[i].isChecked():
                checked.append(self.checkboxes[i])
        if checked != []:
            window = self.parent().parent().parent().parent().parent()
            window.download_clicked(self.title, checked)
            for checkbox in checked:
                checkbox.setChecked(False)
