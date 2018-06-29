# coding=utf-8
# __author__ = 'Mio'
import sys
from math import ceil
from pathlib import Path
sys.path.extend([str(Path(__file__).absolute().parent.parent.parent)])
import io
import PIL
import json
import sqlite3
from contextlib import contextmanager

import cv2
import piexif
import numpy as np
from tornado.log import app_log
from PIL import Image, ImageDraw

import face_recognition
from web_service.settings import TEST_DB_FILE_PATH, IMAGE_FOLDER_PATH


@contextmanager
def db_cursor(db_file_path):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    try:
        yield cursor
    except Exception as e:
        app_log.error(e)
    else:
        conn.commit()
    finally:
        cursor.close()
        conn.close()


class Face(object):
    def __init__(self, file_path, name):
        self.CUBE_WIDTH = 500
        self.THUMBNAIL_SIZE = (self.CUBE_WIDTH, ) * 2
        self.zero_distance = 0
        self.encoding_list_cache = None
        self.locations_cache = None

        self.file_path = file_path
        self.name = name
        self.origin_pil_img = self.prepare_pil_img(self.file_path)
        self.origin_cube_img, self.ratio = self.cube_image()
        # self.old_size = self.origin_pil_img.im.size
        # thumbnail image to speed up
        self.thumb_pil_img = self.thumbnail()

    @property
    def locations(self):
        # get thumbnail locations
        # ensure image contains exact one face
        if self.locations_cache is None:
            locations = face_recognition.face_locations(np.array(self.thumb_pil_img))
            if len(locations) != 1:
                raise Exception(f"image must have one face, not {len(locations)}")
            self.locations_cache = locations

        return self.locations_cache

    def rotate_jpeg(self, pil_img):
        if "exif" in pil_img.info:
            exif_dict = piexif.load(pil_img.info["exif"])

            if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)
                # exif_bytes = piexif.dump(exif_dict)

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

                # origin_pil_img.save(filename, exif=exif_bytes)
        return pil_img

    def prepare_pil_img(self, file_path):
        if isinstance(file_path, (str, Path)):
            pil_img = self.load_image_file(self.file_path)
        elif isinstance(file_path, bytes):
            pil_img = self.load_image_file(io.BytesIO(self.file_path))
        else:
            raise Exception("file_path must be str or bytes")

        return self.rotate_jpeg(pil_img)

    def load_image_file(self, file, mode='RGB'):
        """
        Loads an image file (.jpg, .png, etc) into a numpy array

        :param file: image file name or file object to load
        :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
        :return: image contents
        """
        im = PIL.Image.open(file)
        if mode:
            im = im.convert(mode)
        return im

    def thumbnail(self):
        app_log.info(f"image shape: {self.origin_cube_img.im.size}")
        try:
            thumb_cube_img = self.origin_cube_img.resize(self.THUMBNAIL_SIZE)
        except Exception as e:
            app_log.error(e)
            raise e
        else:
            app_log.info(f"thumbnail shape: {thumb_cube_img.im.size}")
            return thumb_cube_img

    def thumbnail_cv2(self):
        frame = np.array(self.origin_pil_img)[:, :, ::-1]
        cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    def __str__(self):
        return f"{self.name}: {self.zero_distance}"

    def __repr__(self):
        return self.__str__()

    @property
    def origin_location(self):
        # true_origin_location = face_recognition.face_locations(np.array(self.origin_pil_img))
        # app_log.info(f"true_origin_location: {true_origin_location}")
        return [[t * self.ratio for t in location] for location in self.locations]

    @property
    def encoding_list(self):
        """
        cal face encodings
        :return: list
        """
        if self.encoding_list_cache is None:
            app_log.info(f"origin_location: {self.origin_location}")
            self.encoding_list_cache = face_recognition.face_encodings(np.array(self.origin_cube_img), self.origin_location)[0]

        return self.encoding_list_cache

    def cube_image(self):
        max_old_size = max(self.origin_pil_img.size)

        ratio = ceil(max_old_size / self.CUBE_WIDTH)

        size = (ratio*self.CUBE_WIDTH, ) * 2

        cube_im = Image.new('RGB', size)
        cube_im.paste(self.origin_pil_img)
        return cube_im, ratio

    def save(self, saved_file_name=None):
        if saved_file_name:
            self.file_path = IMAGE_FOLDER_PATH/saved_file_name
            self.origin_cube_img.save(self.file_path)
            return self.file_path

    def draw(self, show=False, saved_file_name=None):
        # face_landmarks_list = face_recognition.face_landmarks(self.image, self.locations)
        face_landmarks_list = face_recognition.face_landmarks(np.array(self.origin_cube_img), self.origin_location)
        face_landmarks = face_landmarks_list[0]

        # pil_image = Image.fromarray(self.image)
        pil_image = self.origin_cube_img
        d = ImageDraw.Draw(pil_image, 'RGBA')

        # Make the eyebrows into a nightmare
        top, right, bottom, left = self.locations[0]
        d.rectangle([(left, top), (right, bottom)], outline="red")
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

        only_face = pil_image.crop((left, top, right, bottom))
        if show:
            only_face.show()
            pil_image.show()
        if saved_file_name:
            pil_image.save(IMAGE_FOLDER_PATH/saved_file_name)


class OrmFace(object):
    """
    TODO: ORM of Face
    """

    def __init__(self, id_, name=None, encoding=None, file_path=None):
        self.id_ = id_
        self.name = name
        self.encoding = json.loads(encoding)
        self.file_path = Path(file_path)


class FaceStore(object):
    def __init__(self, load_kwargs=None):
        self.load_all = self.load_all_from_sqlite
        self.load_kwargs = load_kwargs if isinstance(load_kwargs, dict) else dict()

        self.profiles = []
        self.encodings = []

    def load_all_from_sqlite(self):
        before = len(self.profiles)
        exists_id = 0 if not self.profiles else self.profiles[-1].id_
        with db_cursor(str(TEST_DB_FILE_PATH)) as cursor:
            cursor.execute("SELECT id, name, encoding, file_path FROM pickled_faces WHERE id > {} ORDER BY id".format(exists_id))
            rows = cursor.fetchall()
            add_faces = [OrmFace(id_=row[0], name=row[1], encoding=row[2], file_path=row[3]) for row in rows]
            self.profiles.extend(add_faces)
            self.encodings.extend([face.encoding for face in add_faces])
            app_log.info(f"add faces:{len(self.profiles) - before} ;total loaded faces: {len(self.profiles)}")

    def add(self, face: Face):
        with db_cursor(str(TEST_DB_FILE_PATH)) as cursor:
            cursor.execute(f'INSERT INTO pickled_faces (name, encoding, file_path) VALUES ("{face.name}", "{json.dumps(list(face.encoding_list))}", "{face.file_path}")')
            rows = cursor.fetchall()
            app_log.info(list(rows))
        self.load_all_from_sqlite()
        return

        # self.profiles.append(OrmFace())


if __name__ == '__main__':
    print("yes")
    # with db_cursor() as _cursor:
    #     sql = "INSERT INTO pickled_faces(name, encoding, file_path) VALUES (?, ?, ?)"
    #     from web_service.sci.known_faces import known_faces
    #     _params = [(face.name, json.dumps(list(face.encoding_list)), str(face.file_path)) for face in known_faces]
    #     print(_params)
    #     _cursor.executemany(sql, _params)
    fs = FaceStore()
    fs.load_all_from_sqlite()
