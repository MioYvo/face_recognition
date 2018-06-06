# coding=utf-8
# __author__ = 'Mio'
import logging
from contextlib import contextmanager

from sqlalchemy import Column, Integer, Float, DateTime, Text, String
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from generator import settings


@contextmanager
def make_session(session_factory=settings.session_factory):
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(e)
        raise
    finally:
        session.close()


class RstBase(object):
    id = Column(Integer, primary_key=True)
    create_at = Column(type_=DateTime(timezone=False), server_default=func.current_timestamp())
    update_at = Column(type_=DateTime(timezone=False), server_onupdate=func.current_timestamp())
    # effective_date = Column(type_=Date, server_default=func.current_date())
    user_id = Column(type_=String(40), doc="用户id", index=True)


Base = declarative_base(cls=RstBase)


# noinspection NonAsciiCharacters
class SRL(Base):
    # __table_args__ = (
    #     Index('idx_srl_user_id_effective_date', 'user_id', 'effective_date', unique=True),
    # )
    __tablename__ = 'zhdj_ml_srl'

    提升动力 = Column(type_=Float, doc="提升动力 平均值")
    自我控制 = Column(type_=Float, doc="自我控制 平均值")
    挑战与支持 = Column(type_=Float, doc="挑战与支持 平均值")
    自信心 = Column(type_=Float, doc="自信心 平均值")
    理解他人 = Column(type_=Float, doc="理解他人 平均值")
    宽容性 = Column(type_=Float, doc="宽容性 平均值")
    热情 = Column(type_=Float, doc="热情 平均值")
    团队协作 = Column(type_=Float, doc="团队协作 平均值")
    稳定情绪 = Column(type_=Float, doc="稳定情绪 平均值")
    尊敬他人 = Column(type_=Float, doc="尊敬他人 平均值")
    创造性 = Column(type_=Float, doc="创造性 平均值")


# noinspection NonAsciiCharacters
class KTE(Base):
    # __table_args__ = (
    #     Index('idx_kte_user_id_effective_date', 'user_id', 'effective_date', unique=True),
    # )
    __tablename__ = 'zhdj_ml_kte'

    乐群性 = Column(type_=Float, doc="乐群性 平均值")
    聪慧性 = Column(type_=Float, doc="聪慧性 平均值")
    稳定性 = Column(type_=Float, doc="稳定性 平均值")
    持强性 = Column(type_=Float, doc="持强性 平均值")
    兴奋性 = Column(type_=Float, doc="兴奋性 平均值")
    有恒性 = Column(type_=Float, doc="有恒性 平均值")
    敢为性 = Column(type_=Float, doc="敢为性 平均值")
    敏感性 = Column(type_=Float, doc="敏感性 平均值")
    怀疑性 = Column(type_=Float, doc="怀疑性 平均值")
    幻想性 = Column(type_=Float, doc="幻想性 平均值")
    世故性 = Column(type_=Float, doc="世故性 平均值")
    忧虑性 = Column(type_=Float, doc="忧虑性 平均值")
    实验性 = Column(type_=Float, doc="实验性 平均值")
    独立性 = Column(type_=Float, doc="独立性 平均值")
    自律性 = Column(type_=Float, doc="自律性 平均值")
    紧张性 = Column(type_=Float, doc="紧张性 平均值")


class FourMat(Base):
    """
    同一个 user_id effective_date 有多行
    """
    # __table_args__ = (
    # Index('idx_4mat_user_id_effective_date', 'user_id', 'effective_date', unique=True),
    # )
    __tablename__ = 'zhdj_ml_4mat'

    X = Column(type_=Float, doc="X")
    Y = Column(type_=Float, doc="Y")


class FourMat2(Base):
    """
    同一个 user_id effective_date 有多行
    """
    # __table_args__ = (
    #     Index('idx_4mat2_user_id_effective_date', 'user_id', 'effective_date', unique=True),
    # )
    __tablename__ = 'zhdj_ml_4mat2'

    X = Column(type_=Float, doc="X")
    Y = Column(type_=Float, doc="Y")
    dangType = Column(type_=String(20), doc="党性指标", index=True)
    dangTypeValue = Column(type_=Float, doc="党性值")


# noinspection NonAsciiCharacters
class DangNorm(Base):
    # __table_args__ = (
    #     Index('idx_dangnorm_user_id_effective_date', 'user_id', 'effective_date', unique=True),
    # )
    __tablename__ = 'zhdj_ml_dangnorm'

    作风修养 = Column(type_=Float, doc="作风修养")
    宗旨修养 = Column(type_=Float, doc="宗旨修养")
    政治修养 = Column(type_=Float, doc="政治修养")
    理论修养 = Column(type_=Float, doc="理论修养")
    法纪修养 = Column(type_=Float, doc="法纪修养")
    道德修养 = Column(type_=Float, doc="道德修养")


class KnowMsg(Base):
    # __table_args__ = (
    #     Index('idx_know_msg_user_id_effective_date', 'user_id', 'effective_date', 'course_id', unique=True),
    # )
    __tablename__ = 'zhdj_ml_know_msg'

    course_id = Column(type_=Integer, doc="课程id")
    pmi = Column(type_=Text, doc="课程id")


if __name__ == 'local_now__main__':
    print(())
