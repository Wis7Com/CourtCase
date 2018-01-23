#coding=gbk

#��AJsegment���е�ladsrc�дʻ㽨��dictionary��
#�����ݴ���segment2��
#document��ʽ
# {
#     _id(objectId)
#     word(string)��
#     pos(int)����λ��
# }


import pymongo
from bson.objectid import ObjectId

import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='dictionary.log',
                filemode='w')


def getFromMongo(col, fromId):

    nextId = fromId
    tag = 1

    res = list()

    condition = {} if fromId == "0" else {'_id': {'$gt': ObjectId(fromId)}}

    logging.info('This is info message')
    print(col.find(condition).limit(2000).count())
    if col.find(condition).limit(2000).count() == 0:
        tag = 0

    cur = col.find(condition, no_cursor_timeout = True).limit(2000)
    for item in cur:
        res.extend(item['ldasrc'].strip().split(' '))
        nextId = item["_id"]

    cur.close()

    return (nextId, tag, set(res))


def handledata(res, col):
    result = list()
    fromPos = col.count()
    i = fromPos

    if '' in res:
        res.remove('')

    if i == 0:
        for item in res:
            result.append({
                "word": item,
                "pos": i,
            })
            i += 1
    else:
        for item in res:
            if col.find({"word" : item}) == None:
                result.append({
                    "word" : item,
                    "pos" : i,
                })
                i += 1

    logging.info("����д�룺 %d ��" % i)
    return result


def save2mongo(col, res):
    for item in res:
        col.insert(item)

if __name__ == '__main__':
    #�������ݿ�
    con = pymongo.MongoClient('localhost', 27017)
    col1 = con.Lawcase.AJsegment
    col2 = con.Lawcase.dictionary
    # con = pymongo.MongoClient('192.168.68.11', 20000)
    # col1 = con.lawCase.AJsegment
    # col2 = con.lawCase.dictionary

    nextId = "0"

    i = 1
    while True:
        logging.info("�� %s �ζ�����" % str(i))
        (nextId, tag, getRes) = getFromMongo(col1, nextId)
        logging.info("nextId�� %s" % str(nextId))
        logging.info("enter token!")
        afterHadle = handledata(getRes, col2)
        logging.info("exit token!")
        logging.info("exit save!")
        save2mongo(col2, afterHadle)
        logging.info("exit save!")
        i += 1

        if tag == 0:
            break