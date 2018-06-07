# coding=utf-8
# __author__ = 'Mio'

import sys
from pathlib import Path
sys.path.extend([str(Path(__file__).absolute().parent.parent)])

from web_service.sci.persist_face import FaceStore

import tornado.web

from web_service.urls import urls
from web_service.utils.helpers import start_application
from web_service.settings import (
    loop, APP_SETTINGS,
    APP_PORT)


class Configurer(tornado.web.Application):
    def __init__(self):
        self.face_store = FaceStore()
        self.face_store.load_all(**self.face_store.load_kwargs)

        tornado.web.Application.__init__(self, urls, **APP_SETTINGS)

    def stop(self):
        # self.scheduler.stop()
        pass


def run():
    start_application(Configurer, loop, port=APP_PORT)


if __name__ == '__main__':
    run()
