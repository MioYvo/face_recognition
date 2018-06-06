# coding=utf-8
# __author__ = 'Mio'
import asyncio
from os import getenv
from pathlib import Path

# import docker
from pytz import timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tornado.platform.asyncio import AsyncIOMainLoop
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# ---------------------  APP  ---------------------

LOCAL_TZ = getenv("LOCAL_TZ", "Asia/Shanghai")
LOCAL_TZ_OBJ = timezone(LOCAL_TZ)
APP_PORT = int(getenv("APP_PORT", "8888"))

RANDOM_FROM = float(getenv("RANDOM_FROM", 0.7))
RANDOM_TO = float(getenv("RANDOM_TO", 1.0))


SETTINGS_FILE_PATH = Path(__file__).absolute()
APP_PATH = SETTINGS_FILE_PATH.parent
IMAGE_FOLDER_PATH = Path(SETTINGS_FILE_PATH.parent / "static")

# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# if AsyncIOMainLoop.initialized():
#     AsyncIOMainLoop.clear_instance()
# async_ioloop = AsyncIOMainLoop()
# async_ioloop.install()
loop = asyncio.get_event_loop()
# --------------------    docker    --------------------
# DOCKER_SOCK_ADDR = getenv('DOCKER_SOCK_ADDR', "unix://var/run/docker.sock")
# docker_api_client = docker.APIClient(base_url=DOCKER_SOCK_ADDR)
# docker_client = docker.DockerClient(base_url=DOCKER_SOCK_ADDR)
# DOCKER_NETWORK = "cpc_ml_network"
# --------------------    tornado    --------------------
APP_SETTINGS = {
    "template_path": APP_PATH / "templates",
    "static_path": APP_PATH / "static",
    "debug": True,
    "autoreload": True
}

# --------------------     SQLAlchemy    --------------------
# DB_HOST = getenv('DB_HOST', '127.0.0.1')
# DB_PORT = getenv('DB_PORT', '3306')
# DB_NAME = getenv('DB_NAME', 'cpc_ml_scheduler')
# DB_USERNAME = getenv('DB_USERNAME', 'root')
# DB_PASSWORD = getenv('DB_PASSWORD', 'root')
DB_CONN_CHARSET = getenv('DB_CONN_CHARSET', 'utf8')
DB_SQL_ECHO = bool(int(getenv('DB_SQL_ECHO', 0)))

DB_CONNECT_STR = getenv('DB_CONNECT_STR', 'postgresql+psycopg2://postgres:postgres@10.90.3.170:5432/zhdj')

# CONN_POOL_RECYCLE_SECS = int(getenv("CONN_POOL_RECYCLE_SECS", 600))
engine = create_engine(DB_CONNECT_STR, echo=DB_SQL_ECHO, encoding=DB_CONN_CHARSET)
session_factory = sessionmaker(engine)

# -------------------- ap scheduler --------------------
DEFAULT_INTERVAL_SECONDS = 30
APS_TABLENAME = getenv('APS_TABLENAME', 'apscheduler_jobs')

job_defaults = {'coalesce': True}

# jobstores = {
#     'default': SQLAlchemyJobStore(engine=engine, tablename=APS_TABLENAME)
# }
JOB_ID = getenv("JOB_ID", "job_id_{func}")

LOGS_TO_CLOUD_INTERVAL_SECONDS = int(getenv("LOGS_TO_CLOUD_INTERVAL_SECONDS", "10"))

KEY_JOB_LAST_RUN_DT = "scheduler:job:{job_name}:last_run_time"

# --------------------     docker    --------------------
DOCKER_REGISTRY = getenv("GW_DOCKER_REGISTRY", "localhost")

DATA_SOURCE_TYPE_ORACLE = getenv("DATA_SOURCE_TYPE_ORACLE", "oracle").lower()
DATA_SOURCE_TYPE_POWER_SYSTEM = getenv("DATA_SOURCE_TYPE_POWER_SYSTEM", "power-system").lower()
DATA_SOURCE_TYPE_IMC = getenv("DATA_SOURCE_TYPE_IMC", "imc").lower()
IIOT_GW_NETWORK = getenv("IIOT_GW_NETWORK", "iiotgw_default").lower()

DOCKER_IMAGES_PULL = bool(int(getenv("DOCKER_IMAGES_PULL", 0)))
