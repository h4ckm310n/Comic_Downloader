from PyQt5.QtCore import *
import importlib


class InfoThread(QThread):
    info_state = pyqtSignal(int)
    info = pyqtSignal(dict)

    def __init__(self, href, module, cfs, rs):
        super(InfoThread, self).__init__()
        self.href = href
        self.module = module
        self.cfs = cfs
        self.rs = rs

    def run(self):
        self.info_state.emit(0)

        module = importlib.import_module('.' + self.module, 'api')
        if module.request_method == "cfs":
            info = module.info(self.cfs, self.href)
        else:
            info = module.info(self.rs, self.href)

        self.info_state.emit(1)
        self.info.emit(info)
