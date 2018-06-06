# # coding=utf-8
# # __author__ = 'Mio'
# import logging
#
# from web_service.settings import (docker_client, DOCKER_NETWORK,
#                                 DB_ALPHAEYE2_HOST, DB_NOOBIE2_HOST, DB_NOOBIE2_PORT,
#                                 DB_NOOBIE2_NAME, DB_NOOBIE2_USERNAME, DB_NOOBIE2_PASSWORD, DB_NOOBIE2_CONN_CHARSET,
#                                 DB_ALPHAEYE2_PORT, DB_ALPHAEYE2_NAME, DB_ALPHAEYE2_USERNAME, DB_ALPHAEYE2_PASSWORD,
#                                 DB_ALPHAEYE2_CONN_CHARSET, LOCAL_TZ, WORKER_CONTAINER_NAME, WORKER_IMAGE_NAME,
#                                 DB_ZHDJ_CONNECT_STRING, DB_NOOBIE2_TYPE)
#
#
# def rm_exists_container(container_name=WORKER_CONTAINER_NAME):
#     logging.info(f"remove {container_name}")
#     exists_containers = docker_client.containers.list(
#         all=True,
#         filters={"name": container_name}
#     )
#     for container in exists_containers:
#         try:
#             container.stop(timeout=3)
#         except Exception as e:
#             logging.error(e)
#
#         try:
#             container.remove(v=True)
#         except Exception as e:
#             logging.error(e)
#
#
# def restart_container(container_name=DB_ALPHAEYE2_HOST):
#     exists_containers = docker_client.containers.list(
#         all=True,
#         filters={"name": container_name}
#     )
#     for container in exists_containers:
#         try:
#             container.restart()
#         except Exception as e:
#             logging.error(e)
#
#
# def start_worker(image_name=WORKER_IMAGE_NAME, container_name=WORKER_CONTAINER_NAME, docker_network=DOCKER_NETWORK,
#                  auto_remove=False,
#                  db_noobie2_type=DB_NOOBIE2_TYPE,
#                  db_noobie2_host=DB_NOOBIE2_HOST,
#                  db_noobie2_port=DB_NOOBIE2_PORT,
#                  db_noobie2_name=DB_NOOBIE2_NAME,
#                  db_noobie2_username=DB_NOOBIE2_USERNAME,
#                  db_noobie2_password=DB_NOOBIE2_PASSWORD,
#                  db_noobie2_conn_charset=DB_NOOBIE2_CONN_CHARSET,
#                  db_alphaeye2_host=DB_ALPHAEYE2_HOST,
#                  db_alphaeye2_port=DB_ALPHAEYE2_PORT,
#                  db_alphaeye2_name=DB_ALPHAEYE2_NAME,
#                  db_alphaeye2_username=DB_ALPHAEYE2_USERNAME,
#                  db_alphaeye2_password=DB_ALPHAEYE2_PASSWORD,
#                  db_alphaeye2_conn_charset=DB_ALPHAEYE2_CONN_CHARSET,
#                  db_zhdj_connect_string=DB_ZHDJ_CONNECT_STRING,
#                  tz=LOCAL_TZ,
#                  ):
#     db_alphaeye2_connect_url = f"mysql+pymysql://{db_alphaeye2_username}:{db_alphaeye2_password}@{db_alphaeye2_host}:{db_alphaeye2_port}/{db_alphaeye2_name}"
#     if "mysql" in db_alphaeye2_connect_url:
#         db_alphaeye2_connect_url += f"?charset={db_alphaeye2_conn_charset}"
#     db_noobie2_connect_url = f"{db_noobie2_type}://{db_noobie2_username}:{db_noobie2_password}@{db_noobie2_host}:{db_noobie2_port}/{db_noobie2_name}"
#     if "mysql" in db_noobie2_connect_url:
#         db_noobie2_connect_url += f"?charset={db_noobie2_conn_charset}"
#
#     # remove exists ml-worker
#     rm_exists_container(container_name=container_name)
#     restart_container(container_name=db_alphaeye2_host)
#     if db_alphaeye2_host != db_noobie2_host:
#         restart_container(container_name=db_noobie2_host)
#
#     env = {
#         "TZ": tz,
#         "db_alphaeye2": db_alphaeye2_connect_url,
#         "db_noobie2": db_noobie2_connect_url,
#         "DB_ZHDJ_CONNECT_STRING": db_zhdj_connect_string
#     }
#     logging.info(env)
#
#     run_kwargs = dict(
#         image=image_name,
#         name=container_name,
#         # command=parser.attr['command'],
#         network=docker_network,
#         detach=True,
#         auto_remove=auto_remove,
#         environment=env,
#         # links=ds.container_run_args.get('links', {}),
#         restart_policy={"Name": "on-failure", "MaximumRetryCount": 3},
#         log_config={"type": "json-file", "config": {"max-file": "1", "max-size": "10m"}}
#         # ports=parser.attr['ports'],
#         # volumes=parser.attr['volumes']
#     )
#     try:
#         # if detach is True, return a :py:class:`Container` object
#         container = docker_client.containers.run(**run_kwargs)
#         logging.info(f"{container.name}-{container.id} starting")
#     except Exception as e:
#         logging.error("error occurred when starting container: {}".format(e))
#         # log_to_cloud(ds.uuid, str(e))
#         return False, e
#     else:
#         logging.info("container {} started".format(WORKER_CONTAINER_NAME))
#         return True, container
#
#
# if __name__ == '__main__':
#     start_worker()
