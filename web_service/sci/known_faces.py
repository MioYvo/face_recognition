# coding=utf-8
# __author__ = 'Mio'
from web_service.sci.persist_face import Face
from web_service.settings import IMAGE_FOLDER_PATH


known_faces = [
    Face(IMAGE_FOLDER_PATH / "WechatIMG27.jpeg", "王浩宇"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG20.jpeg", "李中平"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG21.jpeg", "刘如斯"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG30.jpeg", "樊长松"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG798.jpeg", "刘波"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG33.jpeg", "唐观平"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG34.jpeg", "阳明亮"),
]

# known_faces_encodings = [face.encoding_list for face in known_faces]

# unknown_face = Face(IMAGE_FOLDER_PATH / "WechatIMG803.jpeg", "Unknown")
# unknown_face.draw()
# rst = face_recognition.face_distance(known_faces_encodings, unknown_face.encoding_list[0])
# print(rst)
