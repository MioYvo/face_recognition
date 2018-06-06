# coding=utf-8
# __author__ = 'Mio'

import sys
from pathlib import Path

from web_service.sci import known_faces

sys.path.extend([str(Path(__file__).absolute().parent.parent)])
import tornado.web

from web_service.urls import urls
from web_service.utils.helpers import start_application
from web_service.settings import (
    loop, APP_SETTINGS,
    APP_PORT)


class Configurer(tornado.web.Application):
    def __init__(self):
        self.known_faces = known_faces
        tornado.web.Application.__init__(self, urls, **APP_SETTINGS)

    def stop(self):
        # self.scheduler.stop()
        pass


def run():
    start_application(Configurer, loop, port=APP_PORT)


if __name__ == '__main__':
    run()
