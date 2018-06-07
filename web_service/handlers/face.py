# coding=utf-8
# __author__ = 'Mio'
from tornado.log import app_log

import face_recognition
# from web_service.sci.known_faces import Face, known_faces_encodings, known_faces
from web_service.sci.persist_face import Face
from web_service.settings import TOLERANCE
from web_service.utils.gtornado.web import BaseRequestHandler


class FaceHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.render("face.html", profiles=self.application.face_store.profiles)

    def post(self):
        unknown = self.request.files.get('unknown')
        if len(unknown) != 1:
            app_log.error("number of unknown picture must be 1")
            self.render("result.html", name="error", tolerance="number of unknown picture must be 1")
            return
        info = unknown[0]
        filename, content_type, body = info['filename'], info['content_type'], info['body']
        try:
            unknown_face = Face(body, "unknown")
        except Exception as e:
            app_log.error(e)
            self.render("result.html", name="error", tolerance=str(e))
            return

        check_rst = face_recognition.face_distance(self.application.face_store.encodings, unknown_face.encoding_list)
        # unknown_face.draw()
        app_log.info(check_rst)

        check_rst_sorted = sorted([(index, value) for index, value in enumerate(check_rst)], key=lambda x: x[1])
        detected_face = self.application.face_store.profiles[check_rst_sorted[0][0]]
        deviation = check_rst_sorted[0][1]
        app_log.info(f"name: {detected_face.name}, deviation: {deviation}, tolerance: {TOLERANCE}")
        print(detected_face.file_path.name)
        self.render("result.html", name=detected_face.name, tolerance=TOLERANCE, deviation=deviation,
                    image_file_name=detected_face.file_path.name)
