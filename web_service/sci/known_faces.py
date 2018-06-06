# coding=utf-8
# __author__ = 'Mio'
import PIL
import io
from functools import reduce
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ExifTags
from tornado.log import app_log

import face_recognition
import piexif

from web_service.settings import IMAGE_FOLDER_PATH


class Face(object):
    def __init__(self, file_path, name):
        self.THUMB_WIDTH = 1000
        self.THUMB_HIGHT = 1000

        self.file_path = file_path
        self.name = name
        if isinstance(file_path, (str, Path)):
            self.image, self.pil_img = self.load_image_file(self.file_path)
        elif isinstance(file_path, bytes):
            self.image, self.pil_img = self.load_image_file(io.BytesIO(self.file_path))
        else:
            raise Exception("file_path must be str or bytes")
        app_log.info(f"image shape: {self.image.shape}")
        if max(self.image.shape) > 1280:
            # self.pil_img.show()

            self.pil_img_thumbnail = self.thumbnail(self.pil_img)
            self.pil_img_thumbnail = self.rotate_jpeg(pil_img=self.pil_img_thumbnail)
            # self.pil_img_thumbnail.show()
            self.image = np.array(self.pil_img_thumbnail)

        self.locations = face_recognition.face_locations(self.image)
        if len(self.locations) != 1:
            raise Exception(f"cant find location {self.locations}")
        self.top, self.right, self.bottom, self.left = self.locations[0]

        self.temp_distance = 100

        self.encoding_list_cache = None

    def rotate_jpeg(self, pil_img):
        if "exif" in pil_img.info:
            exif_dict = piexif.load(pil_img.info["exif"])

            if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)
                exif_bytes = piexif.dump(exif_dict)

                if orientation == 2:
                    pil_img = pil_img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    pil_img = pil_img.rotate(180)
                elif orientation == 4:
                    pil_img = pil_img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 5:
                    pil_img = pil_img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    pil_img = pil_img.rotate(-90, expand=True)
                elif orientation == 7:
                    pil_img = pil_img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    pil_img = pil_img.rotate(90, expand=True)

                # pil_img.save(filename, exif=exif_bytes)
        return pil_img

    def load_image_file(self, file, mode='RGB'):
        """
        Loads an image file (.jpg, .png, etc) into a numpy array

        :param file: image file name or file object to load
        :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
        :return: image contents as numpy array
        """
        im = PIL.Image.open(file)
        if mode:
            im = im.convert(mode)
        return np.array(im), im

    def thumbnail(self, image):
        try:
            # image = Image.open(os.path.join(path, fileName))
            orientation = None
            if hasattr(image, '_getexif'):  # only present in JPEGs
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = dict(image._getexif().items())

                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
                else:
                    pass

                image.thumbnail((self.THUMB_WIDTH, self.THUMB_HIGHT), Image.ANTIALIAS)
                # image.save(os.path.join(path, fileName))
        except Exception as e:
            print(e)
            raise e
        else:
            return image

    def __str__(self):
        return f"{self.name}: {self.temp_distance}"

    def __repr__(self):
        return self.__str__()

    @property
    def encoding_list(self):
        """
        cal face encodings
        :return: list
        """
        if self.encoding_list_cache is None:
            self.encoding_list_cache = face_recognition.face_encodings(self.image, self.locations)

        return self.encoding_list_cache

    def draw(self):
        face_landmarks_list = face_recognition.face_landmarks(self.image, self.locations)
        face_landmarks = face_landmarks_list[0]

        pil_image = Image.fromarray(self.image)
        d = ImageDraw.Draw(pil_image, 'RGBA')

        # Make the eyebrows into a nightmare
        d.rectangle([(self.left, self.top), (self.right, self.bottom)], outline="red")
        d.point(
            face_landmarks['left_eye']
            + face_landmarks['right_eye']
            + face_landmarks['top_lip']
            + face_landmarks['bottom_lip']
            + face_landmarks['nose_tip']
            # + face_landmarks['nose_bridge']
        )

        d.line(face_landmarks['left_eyebrow'], fill="blue")
        d.line(face_landmarks['right_eyebrow'], fill="blue")
        d.line(face_landmarks['chin'])
        d.line(face_landmarks['nose_bridge'])

        only_face = pil_image.crop((self.left, self.top, self.right, self.bottom))
        only_face.show()
        pil_image.show()


known_faces = [
    Face(IMAGE_FOLDER_PATH / "WechatIMG27.jpeg", "王浩宇"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG20.jpeg", "李中平"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG21.jpeg", "刘如斯"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG30.jpeg", "樊长松"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG798.jpeg", "刘波"),
    Face(IMAGE_FOLDER_PATH / "WechatIMG31.jpeg", "唐关平"),
]

known_faces_encodings = reduce(lambda x, y: x + y, [face.encoding_list for face in known_faces])

unknown_face = Face(IMAGE_FOLDER_PATH / "WechatIMG803.jpeg", "Unknown")
unknown_face.draw()
rst = face_recognition.face_distance(known_faces_encodings, unknown_face.encoding_list[0])
print(rst)
# print(IMAGE_FOLDER_PATH / "WechatIMG28.jpeg")
#
# rst = face_recognition.face_distance(reduce(lambda x, y: x + y, [face.encoding_list for face in known_faces]),
#                                      unknown_face.encoding_list[0])
# for r, face in zip(rst, known_faces):
#     face.temp_distance = r
#
# print(sorted(known_faces, key=lambda x: x.temp_distance))
