#coding=gbk

#��paragraph���е�ԭ���߳ơ������ƺͲ�����ʵ��ʹ�ý�ͽ��зִ�
#�����ݴ���segment2��
#document��ʽ
# {
#     _id(objectId)
#     ldasrc(string)lda��ģ��Ҫ
#     defendantArguedԭ���߳ƶ�
#     {
#       token(string)�ִʽ���ֶΣ��ո����
#       flag(string)���Ա�ע�ֶΣ��ո����
#       keywords(string)�ؼ����ֶΣ��ո����
#       tfidfsrc(string)����tfidfֵʹ�õ�����
#       text(string)ԭ��
#     } or None
#     plaintiffAlleges�����ƶ�
#     factFound������ʵ��
#     tag(boolean)�������ζ���ΪNoneΪtrue������Ϊfalse
#     fulltextid(string)lawcase����ԭ��id
# }


import pymongo
from bson.objectid import ObjectId
from jieba import analyse, posseg
import re

import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='AJSegment1.log',
                filemode='w')

textrank = analyse.textrank
analyse.set_stop_words("stopWords.txt")

def getFromMongo(col, fromId):

    nextId = fromId
    tag = 1

    res = list()

    condition = {} if fromId == "0" else {'_id': {'$gt': ObjectId(fromId)}}

    logging.info('This is info message')
    print(col.find(condition).limit(12500).count())
    if col.find(condition).limit(12500).count() == 0:
        tag = 0

    #i = 0
    j = 0
    cur = col.find(condition, no_cursor_timeout = True).limit(12500)
    for item in cur:
        nextId = item["_id"]

        doc = dict()
        doc['fulltextid'] = item['fullTextId']
        doc['fulltag'] = False
        doc['tag'] = item['tag']
        doc['title'] = item['title']

        if doc['tag'] == '1' or doc['tag'] == '2':
            plaintiffAlleges = item['plaintiffAlleges']
            if isinstance(plaintiffAlleges, dict):
                p = dict()
                if re.match(r'[0-9a-zA-Z]+', plaintiffAlleges['text']) == None:
                    p['text'] = plaintiffAlleges['text']
                    doc['plaintiffAlleges'] = p
                else:
                    doc['plaintiffAlleges'] = None
            else:
                doc['plaintiffAlleges'] = None

            defendantArgued = item['defendantArgued']
            if isinstance(defendantArgued, dict):
                d = dict()
                if re.match(r'[0-9a-zA-Z]+', defendantArgued['text']) == None:
                    d['text'] = defendantArgued['text']
                    doc['defendantArgued'] = d
                else:
                    doc['defendantArgued'] = None
            else:
                doc['defendantArgued'] = None

            factFound = item['factFound']
            if isinstance(factFound, dict):
                f = dict()
                if re.match(r'[0-9a-zA-Z]+', factFound['text']) == None:
                    f['text'] = factFound['text']
                    doc['factFound'] = f
                else:
                    doc['factFound'] = None
            else:
                doc['factFound'] = None

            # i += 1
            # print(i)

            if doc['plaintiffAlleges'] == None and doc['defendantArgued'] == None and doc['factFound'] == None:
                # logging.info("��Ч���� %s" % doc['fulltextid'])
                j += 1
                continue
            if doc['plaintiffAlleges'] != None and doc['defendantArgued'] != None and doc['factFound'] != None:
                doc['fulltag'] = True

            res.append(doc)

        # print(i)
        # i+=1
    cur.close()
    logging.info("���� %d ������" % len(res))
    logging.info("%d ����Ч����" % j)

    return (nextId, tag, res)


def handledata(res):
    i = 0
    for doc in res:
        ldasrc = ""
        if doc['plaintiffAlleges'] != None and len(doc['plaintiffAlleges']['text'])>15:
            token, flag, keywords, tfidfSrc = tokenP(doc['plaintiffAlleges']['text'])
            doc['plaintiffAlleges']['token'] = token
            doc['plaintiffAlleges']['flag'] = flag
            doc['plaintiffAlleges']['keywords'] = keywords
            doc['plaintiffAlleges']['tfidfSrc'] = tfidfSrc
            ldasrc = ldasrc + tfidfSrc + ' '

        if doc['defendantArgued'] != None and len(doc['defendantArgued']['text'])>15:
            token, flag, keywords, tfidfSrc = tokenP(doc['defendantArgued']['text'])
            doc['defendantArgued']['token'] = token
            doc['defendantArgued']['flag'] = flag
            doc['defendantArgued']['keywords'] = keywords
            doc['defendantArgued']['tfidfSrc'] = tfidfSrc
            ldasrc = ldasrc + tfidfSrc + ' '

        if doc['factFound'] != None and len(doc['factFound']['text'])>15:
            token, flag, keywords, tfidfSrc = tokenP(doc['factFound']['text'])
            doc['factFound']['token'] = token
            doc['factFound']['flag'] = flag
            doc['factFound']['keywords'] = keywords
            doc['factFound']['tfidfSrc'] = tfidfSrc
            ldasrc = ldasrc + tfidfSrc + ' '

        doc['ldasrc'] = ldasrc.strip()

        i += 1
    logging.info("����д�룺 %d ��" % i)
    return res


def tokenP(paragraph):
    tokenRes = list()
    flagRes = list()
    tfidfSrc = list()

    for word,flag in posseg.cut(paragraph):
        tokenRes.append(word)
        flagRes.append(flag)

    filterFlag = ('n', 'nz', 'nt', 'nl', 'ng', 'v', 'vd', 'vn', 'vi', 'vl', 'vg', 'v', 'vn', 'an', 'b', 'bl', 'd')
    keywordsRes = textrank(paragraph,topK=200,allowPOS=filterFlag)

    for item in tokenRes:
        if item in keywordsRes:
            tfidfSrc.append(item)

    return ((' ').join(tokenRes), (' ').join(flagRes), (' ').join(keywordsRes), (' ').join(tfidfSrc),)

def tokenP1(paragraph):
    tokenRes = list()
    flagRes = list()
    tfidfSrc = list()

    for word,flag in posseg.cut(paragraph):
        tokenRes.append(word)
        flagRes.append(flag)

    filterFlag = ('n', 'nz', 'nt', 'ns', 'nl', 'ng', 'v', 'vd', 'vn', 'vi', 'vl', 'vg', 'v', 'vn', 'an', 'b', 'bl', 'd')
    keywordsRes = textrank(paragraph,topK=200,allowPOS=filterFlag)

    for (word, flag) in zip(tokenRes, flagRes):
        if flag in filterFlag and len(word)>1:
            tfidfSrc.append(word)

    return ((' ').join(tokenRes), (' ').join(flagRes), (' ').join(keywordsRes), (' ').join(tfidfSrc),)



def save2mongo(col, res):
    for item in res:
        col.insert(item)

if __name__ == '__main__':
    #�������ݿ�
    # con = pymongo.MongoClient('localhost', 27017)
    # col1 = con.Lawcase.paragraph
    # col2 = con.Lawcase.AJsegment1
    con = pymongo.MongoClient('192.168.68.11', 20000)
    col1 = con.divorceCase.lawcase
    col2 = con.divorceCase.AJsegment

    nextId = "0"

    i = 1
    #while True:
    logging.info("�� %s �ζ�����" % str(i))
    (nextId, tag, getRes) = getFromMongo(col1, nextId)
    logging.info("nextId�� %s" % str(nextId))
    logging.info("enter token!")
    afterHadle = handledata(getRes)
    logging.info("exit token!")
    logging.info("exit save!")
    save2mongo(col2, afterHadle)
    logging.info("exit save!")
    i += 1

        # if tag == 0:
        #     break