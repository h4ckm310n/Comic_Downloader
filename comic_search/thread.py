from PyQt5.QtCore import *
import api
import importlib


class SearchThread(QThread):

    state = pyqtSignal(int)
    result = pyqtSignal(list)

    def __init__(self, kw, cfs, rs):
        super(SearchThread, self).__init__()
        self.kw = kw
        self.cfs = cfs
        self.rs = rs
        self.results_lst = []

    def run(self):
        self.state.emit(0)  # start search

        """search codes(cases), if none emit(-1)"""
        # search in every module
        for module in api.comic_modules()['modules']:
            if not module['enable']:
                continue
            module = importlib.import_module('.' + module['name'], 'api')
            if module.request_method == "cfs":
                results = module.search(self.cfs, self.kw)
            else:
                results = module.search(self.rs, self.kw)
            if results == -1:
                continue
            for result in results:
                self.results_lst.append(result)
        if self.results_lst == []:
            self.state.emit(-1)
        else:
            self.state.emit(1)  # end search
            self.result.emit(self.results_lst)
