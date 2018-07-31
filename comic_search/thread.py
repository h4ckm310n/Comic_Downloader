from PyQt5.QtCore import *
import requests


class SearchThread(QThread):

    state = pyqtSignal(int)
    result = pyqtSignal(list)

    def __init__(self, text):
        super(SearchThread, self).__init__()
        self.page = 0
        self.url_init = 'http://v2api.dmzj.com/search/show/0/' + text + '/'
        self.comics = []

    def run(self):
        self.state.emit(0)

        while True:
            result = requests.get(self.url_init + str(self.page) + '.json')
            if result.text == '[]':
                if self.page == 0:
                    self.state.emit(1)
                else:
                    break
            else:
                for comic_json in result.json():

                    title = comic_json['title']
                    auth = comic_json['authors']
                    latest = comic_json['last_name']
                    status = comic_json['status']
                    id = comic_json['id']

                    comic = {'title': title, 'auth': auth, 'latest': latest, 'status': status, 'id': id}

                    self.comics.append(comic)
                self.page += 1

        self.state.emit(3)
        self.result.emit(self.comics)
