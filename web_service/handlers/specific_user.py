# coding=utf-8
# __author__ = 'Mio'
import logging
from random import uniform

from web_service.settings import engine, RANDOM_TO, RANDOM_FROM
from web_service.utils.gtornado.web import BaseRequestHandler
# from web_service.models import KTE, FourMat, FourMat2, SRL, KnowMsg, DangNorm, make_session


class Handler(BaseRequestHandler):
    def get(self):
        pass

    def post(self):
        pass

    def put(self):
        pass


class SpecificUserHandler(BaseRequestHandler):
    def get(self, login_name, data_type):
        if data_type not in {"kte", "4mat", "4mat2", "dangnorm", "know_msg", "kte", "srl"}:
            self.write_parse_args_failed_response("date_type no valid")
            return

        func = getattr(Generate, data_type)

        if login_name == "all":
            users = engine.execute(f"SELECT * FROM zhdj_sm_user").fetchall()
            with make_session() as session:
                for user in users:
                    session.add(func(user.id))
        else:
            user = engine.execute(f"SELECT * FROM zhdj_sm_user WHERE login_name={login_name}").fetchone()
            if not user:
                self.write_not_found_entity_response(f"user with login_name {login_name} not found")
                return
            func(user.id, commit=True)


class Generate(object):
    @staticmethod
    def random_score():
        return uniform(RANDOM_FROM, RANDOM_TO)

    @classmethod
    def kte(cls, user_id, commit=False):
        instance = KTE(
            user_id=user_id,
            乐群性=cls.random_score(),
            聪慧性=cls.random_score(),
            稳定性=cls.random_score(),
            持强性=cls.random_score(),
            兴奋性=cls.random_score(),
            有恒性=cls.random_score(),
            敢为性=cls.random_score(),
            敏感性=cls.random_score(),
            怀疑性=cls.random_score(),
            幻想性=cls.random_score(),
            世故性=cls.random_score(),
            忧虑性=cls.random_score(),
            实验性=cls.random_score(),
            独立性=cls.random_score(),
            自律性=cls.random_score(),
            紧张性=cls.random_score(),
        )
        if commit:
            with make_session() as session:
                session.add(instance)

        return instance


if __name__ == '__main__':
    # login_name = "liuli"
    # user = engine.execute(f"SELECT * FROM zhdj_sm_user WHERE login_name='{login_name}'").fetchone()
    # user = dict(user)
    # print(user.fetchone)
    Generate.kte('1e85758820c68b0bacc53dde195a4fd')
