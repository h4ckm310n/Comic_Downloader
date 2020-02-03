from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from comic_download.thread import *
from comic_download import dl_state_dict


class DLList(QListWidget):
    """download list"""

    def __init__(self, parent):
        super(DLList, self).__init__(parent)
        self.setGeometry(20, 12, 740, 470)
        self.items = {}

    def add_to_list(self, frame):
        self.items[frame.index] = QListWidgetItem(self)
        self.items[frame.index].setSizeHint(QSize(738, 35))
        self.addItem(self.items[frame.index])
        self.setItemWidget(self.items[frame.index], frame)
        self.repaint()

    def del_task(self, index):
        self.takeItem(self.row(self.items[index]))
        del self.items[index]
        self.repaint()


class ItemFrame(QFrame):
    """display each download task"""

    def __init__(self, task, parent):
        super(ItemFrame, self).__init__(parent)
        self.setGeometry(0, 0, 738, 35)
        self.index = task['index']
        self.title = task['comic']
        self.chap = task['chap']
        self.state = task['state']
        self.page_num = task['page_num']

        self.title_label = QLabel(' '.join((self.title, self.chap)), self)
        self.title_label.setGeometry(10, 10, 351, 16)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(320, 7, 251, 23)
        self.state_label = QLabel(self)
        self.state_label.setGeometry(580, 10, 61, 16)
        self.progress.setMaximum(self.page_num)
        self.progress.setValue(task['progress'])
        self.pause_label = PauseLabel(self)
        self.del_label = DelLabel(self)
        self.state_change(task['state'])

    def state_change(self, state):
        if state == dl_state_dict['waiting']:
            text = '等待下载'
            self.pause_label.hide()
            self.pause_label.setDisabled(True)
            self.del_label.show()
            self.del_label.setDisabled(False)
        elif state == dl_state_dict['analyzing']:
            text = '正在解析'
            self.pause_label.show()
            self.pause_label.setDisabled(False)
            self.del_label.hide()
            self.del_label.setDisabled(True)
        elif state == dl_state_dict['downloading']:
            text = '正在下载'
        elif state == dl_state_dict['finished']:
            text = '下载完成'
            self.pause_label.hide()
            self.pause_label.setDisabled(True)
            self.del_label.show()
            self.del_label.setDisabled(False)
        elif state == dl_state_dict['pause']:
            text = '暂停下载'
        else:
            text = '下载错误'
            self.pause_label.hide()
            self.pause_label.setDisabled(True)
            self.del_label.show()
            self.del_label.setDisabled(False)

        self.state_label.setText(text)
        self.state = state

    def progress_update(self, count, value):
        if self.page_num == 1:
            self.page_num = count
            self.progress.setMaximum(self.page_num)
        self.progress.setValue(value)

    def pause(self, flag):
        if flag == 0:
            pass
        if flag == 1:
            self.parent().parent().parent().parent().parent().parent().pause_dl(self.index)

    def del_task(self):
        self.parent().parent().del_task(self.index)
        self.parent().parent().parent().parent().parent().parent().del_task(self.index)
        self.deleteLater()
        self = None

    def mousePressEvent(self, a0):
        pass


class PauseLabel(QLabel):
    def __init__(self, parent):
        super(PauseLabel, self).__init__(parent)
        # 0: downloading, 1: paused
        self.flag = 0
        self.setText('暂停')
        self.setGeometry(640, 10, 40, 16)
        self.hide()
        self.setDisabled(True)

    def mousePressEvent(self, a0):
        self.state_change()

    def state_change(self):
        # pause
        if self.flag == 0:
            self.flag = 1
            self.setText('恢复')
            self.show()
            self.setDisabled(False)
            self.parent().del_label.show()
            self.parent().del_label.setDisabled(False)
            self.parent().state_change(dl_state_dict['pause'])
            self.parent().pause(self.flag)

        # resume
        elif self.flag == 1:
            self.flag = 0
            self.setText('暂停')
            self.parent().state_change(dl_state_dict['waiting'])
            self.parent().parent().parent().parent().parent().parent().parent().resume_dl(self.parent().index)


class DelLabel(QLabel):
    def __init__(self, parent):
        super(DelLabel, self).__init__(parent)
        self.setText('删除')
        self.setGeometry(680, 10, 40, 16)
        self.hide()
        self.setDisabled(True)

    def mousePressEvent(self, a0):
        self.parent().del_task()


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
            a0.accept()


class AllPauseButton(QPushButton):
    """Pause all tasks"""

    def __init__(self, parent):
        super(AllPauseButton, self).__init__(parent)
        self.flag = 0
        self.hide()
        self.setDisabled(True)

    def flag_change(self, flag):
        """0 pause, 1 resume"""

        if flag == 0:
            self.setText("全部暂停")
        else:
            self.setText("全部继续")
        self.flag = flag
