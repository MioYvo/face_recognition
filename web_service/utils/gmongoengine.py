# coding=utf-8
# __author__ = 'Mio'
import logging

from bson import ObjectId
from datetime import datetime
from gateway.utils.gtz import datetime_2_string
from mongoengine import EmbeddedDocument, Document, DateTimeField, DynamicEmbeddedDocument
from mongoengine.errors import MultipleObjectsReturned, DoesNotExist


def field_to_json(value):
    ret = value
    if isinstance(value, ObjectId):
        ret = str(value)
    elif isinstance(value, datetime):
        ret = datetime_2_string(value)
    elif isinstance(value, EmbeddedDocument):
        if hasattr(value, "format_response"):
            ret = value.format_response()
    elif isinstance(value, Document):
        if hasattr(value, "format_response"):
            ret = value.format_response()
        else:
            ret = str(value.id)
    elif isinstance(value, list):
        ret = [field_to_json(_) for _ in value]
    elif isinstance(value, dict):
        ret = {k: field_to_json(v) for k, v in value.items()}
    return ret


class BaseDocument(Document):
    # auto
    create_time = DateTimeField(default=datetime.utcnow, help_text="创建时间")
    update_time = DateTimeField(default=None, help_text="创建时间")
    meta = {
        'allow_inheritance': True,
        'abstract': True,
    }

    def format_response(self, skip_fields=None):
        json_data = {}
        for field in self:
            value = self[field]
            value = field_to_json(value)
            if skip_fields is None:
                skip_fields = ['_cls']
            else:
                skip_fields.append('_cls')
            if field in skip_fields:
                continue
            json_data[field] = value
        return json_data

    def save(self, *args, **kwargs):
        self.update_time = datetime.utcnow()
        return super(BaseDocument, self).save(*args, **kwargs)

    @classmethod
    def get(cls, *args, **kwargs):
        try:
            result = cls.objects(*args, **kwargs).get()
        except MultipleObjectsReturned as e:
            logging.error(e.args)
            return cls.objects(*args, **kwargs).first()
        except DoesNotExist as e:
            logging.error(e.args)
            return None
        else:
            return result


class BaseDynamicEmbeddedDocument(DynamicEmbeddedDocument):
    meta = {
        'allow_inheritance': True,
        'abstract': True,
    }

    def format_response(self, skip_fields=None):
        json_data = {}
        for field in self:
            value = self[field]
            value = field_to_json(value)
            if skip_fields is None:
                skip_fields = ['_cls']
            else:
                skip_fields.append('_cls')
            if field in skip_fields:
                continue
            json_data[field] = value
        return json_data


class BaseEmbeddedDocument(EmbeddedDocument):
    # auto
    meta = {
        'allow_inheritance': True,
        'abstract': True,
    }

    def format_response(self, skip_fields=None):
        json_data = {}
        for field in self:
            value = self[field]
            value = field_to_json(value)
            if skip_fields is None:
                skip_fields = ['_cls']
            else:
                skip_fields.append('_cls')
            if field in skip_fields:
                continue
            json_data[field] = value
        return json_data


MAX_COUNT = 100


def paginator(queryset, page, count, limit=True):
    if count > MAX_COUNT or count <= 0:
        count = MAX_COUNT
    if page <= 0:
        page = 1

    amount = queryset.count()

    if not limit:
        content = queryset
    else:
        start = (page - 1) * count
        end = start + count
        content = queryset[start:end]

    return amount, content
