from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class DLList(QListWidget):
    """download list"""

    def __init__(self, parent):
        super(DLList, self).__init__(parent)
        self.setGeometry(20, 12, 740, 470)

    def add_to_list(self, frame):
        item = QListWidgetItem(self)
        item.setSizeHint(QSize(738, 35))
        self.addItem(item)
        self.setItemWidget(item, frame)
        self.repaint()

        
class ItemFrame(QFrame):
    """display each download task"""

    def __init__(self, title, chap, page_num, progress, state, parent):
        super(ItemFrame, self).__init__(parent)
        self.setGeometry(0, 0, 738, 35)
        self.title = title
        self.chap = chap
        self.state = state
        self.page_num = page_num

        self.title_label = QLabel(' '.join((self.title, self.chap)), self)
        self.title_label.setGeometry(10, 10, 351, 16)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(380, 7, 261, 23)
        self.state_label = QLabel(self)
        self.state_change(state)
        self.state_label.setGeometry(660, 10, 61, 16)
        self.progress.setMaximum(self.page_num)
        self.progress.setValue(progress)

    def state_change(self, state):
        if state == -1:
            text = '等待下载'
        elif state == 0:
            text = '正在解析'
        elif state == 1:
            text = '正在下载'
        elif state == 2:
            text = '下载完成'
        else:
            text = '下载错误'

        self.state_label.setText(text)
        self.state = state

    def progress_update(self, count, value):
        if self.page_num == 1:
            self.page_num = count
            self.progress.setMaximum(self.page_num)
        self.progress.setValue(value)

    def mousePressEvent(self, a0):
        pass


class InitDialog(QDialog):
    """wait until the initialization is finished"""

    def __init__(self, parent):
        super(InitDialog, self).__init__(parent)
        self.setGeometry(600, 300, 184, 53)
        self.label = QLabel("正在初始化，请稍等……", self)
        self.label.setGeometry(30, 10, 150, 20)
        self.label.setAlignment(Qt.AlignCenter)
        self.closable = 0

    def closeEvent(self, a0):
        if self.closable == 0:
            a0.ignore()
        elif self.closable == 1:
            pass
