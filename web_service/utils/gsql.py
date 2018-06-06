# coding=utf-8
# __author__ = 'Mio'


def makeDictFactory(cursor):
    columnNames = [d[0].lower() for d in cursor.description]

    def createRow(*args):
        return dict(zip(columnNames, args))

    return createRow
