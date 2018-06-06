# coding=utf-8
# __author__ = 'Mio'
import signal
from functools import partial

import tornado.ioloop
from tornado.log import app_log as logging
from tornado.options import define, parse_command_line, options
from tornado.platform.asyncio import AsyncIOMainLoop

# define("port", default=8888, help="run on the given port", type=int)
# define("debug", default=False, help="run in debug mode")


# noinspection PyUnusedLocal
def signal_handler(server, app, sig, frame):
    """Triggered when a signal is received from system."""
    _ioloop = tornado.ioloop.IOLoop.instance()

    def shutdown():
        """Force server and ioloop shutdown."""
        logging.info('Shutting down server')
        app.stop()
        AsyncIOMainLoop().stop()
        server.stop()
        _ioloop.stop()

    logging.warning('Caught signal: %s', sig)
    _ioloop.add_callback_from_signal(shutdown)


def start_application(app, loop, port=None):
    """Start a tornado application."""
    parse_command_line()
    _app = app()

    _server = _app.listen(port)
    logging.info(f"Running on port {port}")

    signal.signal(signal.SIGTERM,
                  partial(signal_handler, _server, _app))
    signal.signal(signal.SIGINT,
                  partial(signal_handler, _server, _app))

    loop.run_forever()
