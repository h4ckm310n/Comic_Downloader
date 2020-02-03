from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


def search_state(search_dialog, state):
    if state == 1:
        search_dialog.closable = 2
        search_dialog.close()

    if state == 0:
        # searching
        search_dialog.exec_()

    elif state == -1:
        # no results
        search_state(search_dialog, 1)
        text = "没有结果"
        button_text = '确定'
        role = QMessageBox.AcceptRole
        box = QMessageBox(QMessageBox.Information, '', text)
        box.addButton(QPushButton(button_text), role)
        box.exec_()


class SearchDialog(QDialog):
    """wait until the search job is finished"""

    def __init__(self, parent):
        super(SearchDialog, self).__init__(parent)

        self.setObjectName("SearchDialog")
        self.setFixedSize(231, 120)
        self.setWindowTitle("正在搜索")
        self.activateWindow()

        self.closable = 0

        self.label = QLabel(self)
        self.label.setGeometry(30, 20, 171, 21)
        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(130, 80, 81, 32)

        self.label.setText("正在搜索，请稍等……")
        self.pushButton.setText("取消搜索")

        self.pushButton.clicked.connect(self.cancel)

    def cancel(self):
        """cancel the search"""

        self.closable = 1
        self.close()

    def closeEvent(self, a0):
        if self.closable == 0:
            a0.ignore()
        elif self.closable == 1:
            self.closable = 0
            self.parent().search_thread.terminate()
        elif self.closable == 2:
            self.closable = 0


class ResultList(QListWidget):
    def __init__(self, parent):
        super(ResultList, self).__init__(parent)
        self.setObjectName('ResultList')
        self.setGeometry(20, 12, 740, 494)

        self.result_frame = None
        self.result_item = None

        self.result = None

    def add_to_list(self, result):
        self.result = result
        self.result_frame = ResultFrame(self)
        self.result_item = QListWidgetItem(self)
        self.result_item.setSizeHint(QSize(738, 80))
        self.addItem(self.result_item)
        self.setItemWidget(self.result_item, self.result_frame)


class ResultFrame(QFrame):
    def __init__(self, parent):
        super(ResultFrame, self).__init__(parent)
        self.title = self.parent().result['title']
        self.auth = self.parent().result['auth']
        self.latest = self.parent().result['latest']
        self.status = self.parent().result['status']
        self.href = self.parent().result['href']
        self.module = self.parent().result['module']
        self.site = self.parent().result['site']

        self.title_label = TitleLabel(self)
        self.auth_label = QLabel(self)
        self.latest_label = QLabel(self)
        # self.status_label = QLabel(self)
        self.site_label = QLabel(self)

        self.setObjectName('ResultFrame')
        self.setFixedSize(738, 80)
        self.setFrameShape(QFrame.WinPanel)

        self.set_widgets()

    def set_widgets(self):
        self.auth_label.setObjectName('auth_label')
        self.latest_label.setObjectName('latest_label')
        # self.status_label.setObjectName('status_label')

        self.auth_label.setGeometry(20, 50, 150, 16)
        self.auth_label.setText('作者：' + self.auth)

        self.latest_label.setGeometry(190, 50, 200, 16)
        self.latest_label.setText('最新：' + self.latest)

        #self.status_label.setGeometry(450, 50, 51, 16)
        # self.status_label.setText(self.status)

        self.site_label.setGeometry(520, 50, 150, 16)
        self.site_label.setText(self.site)

    def mousePressEvent(self, a0):
        pass


class TitleLabel(QLabel):
    def __init__(self, parent):
        super(TitleLabel, self).__init__(parent)
        self.setObjectName('TitleLabel')
        self.setGeometry(20, 10, 700, 31)
        self.title = \
            '<html><head/><body><p><span style=" font-size:18pt; font-weight:600; color:#0000ff;">'\
            + self.parent().title + '</span></p></body></html>'
        self.setText(self.title)

    def mousePressEvent(self, ev):
        href = self.parent().href
        module = self.parent().module
        window = self.parent().parent().parent().parent().parent().parent().parent()
        window.comic_clicked(href, module)
