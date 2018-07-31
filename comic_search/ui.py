from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


def search_state(search_dialog, state):
    if state == 3:
        search_dialog.close()

    if state == 0:
        # searching
        search_dialog.exec_()

    elif state == 1:
        # no results
        search_state(search_dialog, 3)
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

        self.label = QLabel(self)
        self.label.setGeometry(30, 20, 171, 21)
        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(130, 80, 81, 32)

        self.label.setText("正在搜索，请稍等……")
        self.pushButton.setText("取消搜索")

        self.pushButton.clicked.connect(self.cancel)

    def cancel(self):
        """cancel the search"""

        self.close()

    def closeEvent(self, a0: QCloseEvent):
        self.parent().search_thread.exit()


class ResultList(QListWidget):
    def __init__(self, parent):
        super(ResultList, self).__init__(parent)
        self.setObjectName('ResultList')
        self.setGeometry(20, 12, 740, 494)

        self.result_frame = None
        self.result_item = None

        self.title = None
        self.auth = None
        self.latest = None
        self.status = None
        self.id = None

    def add_to_list(self, title, auth, latest, status, id):
        self.title = title
        self.auth = auth
        self.latest = latest
        self.status = status
        self.id = id
        self.result_frame = ResultFrame(self)
        self.result_item = QListWidgetItem(self)
        self.result_item.setSizeHint(QSize(738, 80))
        self.addItem(self.result_item)
        self.setItemWidget(self.result_item, self.result_frame)


class ResultFrame(QFrame):
    def __init__(self, parent):
        super(ResultFrame, self).__init__(parent)
        self.title = self.parent().title
        self.auth = self.parent().auth
        self.latest = self.parent().latest
        self.status = self.parent().status
        self.id = self.parent().id

        self.title_label = TitleLabel(self)
        self.auth_label = QLabel(self)
        self.latest_label = QLabel(self)
        self.status_label = QLabel(self)

        self.setObjectName('ResultFrame')
        self.setFixedSize(738, 80)
        self.setFrameShape(QFrame.WinPanel)

        self.set_widgets()

    def set_widgets(self):
        self.auth_label.setObjectName('auth_label')
        self.latest_label.setObjectName('latest_label')
        self.status_label.setObjectName('status_label')

        self.auth_label.setGeometry(20, 50, 191, 16)
        self.auth_label.setText('作者：' + self.auth)

        self.latest_label.setGeometry(220, 50, 261, 16)
        self.latest_label.setText('最新：' + self.latest)

        self.status_label.setGeometry(620, 50, 51, 16)
        self.status_label.setText(self.status)


class TitleLabel(QLabel):
    def __init__(self, parent):
        super(TitleLabel, self).__init__(parent)
        self.setObjectName('TitleLabel')
        self.setGeometry(20, 10, 571, 31)
        self.title = \
            '<html><head/><body><p><span style=" font-size:18pt; font-weight:600; color:#0000ff;">'\
            + self.parent().title + '</span></p></body></html>'
        self.setText(self.title)

    def mousePressEvent(self, ev):
        title = self.parent().title
        auth = self.parent().auth
        latest = self.parent().latest
        status = self.parent().status
        id = self.parent().id

        window = self.parent().parent().parent().parent().parent().parent().parent()
        window.comic_clicked(title, auth, latest, status, id)
