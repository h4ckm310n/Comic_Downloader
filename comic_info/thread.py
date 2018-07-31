import requests
from PyQt5.QtCore import *


class InfoThread(QThread):
    info_state = pyqtSignal(int)
    info = pyqtSignal(dict)

    def __init__(self, title, auth, latest, status, id):
        super(InfoThread, self).__init__()

        self.title = title
        self.cover = None
        self.auth = auth
        self.latest = latest
        self.status = status
        self.intro = None
        self.id = id
        self.url = 'http://v2api.dmzj.com/comic/' + str(self.id) + '.json'
        self.chaps = None

    def run(self):
        self.info_state.emit(0)
        r = requests.get(self.url)

        info_json = r.json()
        cover_url = info_json['cover']
        headers = {'referer': self.url}
        r_cover = requests.get(cover_url, headers=headers)
        self.cover = r_cover.content
        self.intro = info_json['description']
        self.chaps = info_json['chapters'][0]['data']
        self.chaps.reverse()
        info = {'title': self.title,
                'cover': self.cover,
                'auth': self.auth,
                'latest': self.latest,
                'status': self.status,
                'intro': self.intro,
                'chaps': self.chaps,
                'id': self.id}

        self.info_state.emit(3)
        self.info.emit(info)
