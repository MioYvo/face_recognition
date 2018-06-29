# coding=utf-8
# __author__ = 'Mio'
from web_service.handlers.specific_user import Handler, SpecificUserHandler
from web_service.handlers.face import FaceHandler, StoreFaceHandler

urls = [
    # (r"^/$", Handler),
    # (r"/schedule/fe/wholesale_ec/package/(\w+)$", shop.OnePackageHandler),
    (r"^/$", FaceHandler),
    (r"^/([\w-]+)/([\w-]+)$", SpecificUserHandler),
    (r"^/store$", StoreFaceHandler),
]
