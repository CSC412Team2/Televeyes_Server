from flask import Flask, jsonify, logging, Response, request
import sys
from flask_pymongo import PyMongo
import utils
from bson import json_util
import os
import math
import re


#This file is the actual server

app = Flask('televeyes')
app.config['MONGO_URI'] = 'mongodb://heroku_7plvr14k:ssqu1unoucs4diblm9n1p81p1u@ds139448.mlab.com:39448/heroku_7plvr14k'
mongo = PyMongo(app)

port = int(os.environ.get('PORT', 5000))
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/', methods=['GET'])
def default():
    return "default"

@app.route('/show/<int:show>', methods=['GET'])
def getShow(show):
    print(show)
    ret = json_util.dumps(mongo.db.shows.find_one_or_404({'id' : show}, {'_id': False, 'ngrams' : False}))
    resp = Response(response=ret,
                    status=200,
                    mimetype="application/json")
    return resp

@app.route('/search/<string:name>', methods=['GET'])
def search(name):
    query = utils.make_ngrams(name)
    ret = json_util.dumps(mongo.db.shows.find(
        {
            "$text": {
                "$search": str(query)
            }
        },
        {
            "_id" : False,
            "ngrams" : False,
            "score": {
                "$meta": "textScore"
            }
        }
    ).sort([("score", {"$meta": "textScore"})]
    ))
    resp = Response(response=ret,
                    status=200,
                    mimetype="application/json")
    return resp

@app.route('/category/<string:cat>', methods=['GET'])
def category(cat):
    size = 50

    cur = mongo.db.shows.find(
        {
            "genres": cat
        },
        {
            "_id" : False,
            "ngrams" : False
        }
    ).sort([('premiered' , 1)])

    count = cur.count()

    page = request.args.get('page', 1)

    if not re.match('^[0-9]+$', str(page)):
        page = 1

    page = int(page)

    if (page * size) > count:
        return Response(status=404)

    if page != 1:
        cur.skip(size * (page - 1))

    cur.limit(size)

    ret = json_util.dumps(cur)

    resp = Response(response=ret,
                    status=200,
                    mimetype="application/json")
    return resp

#app.run(host='0.0.0.0', port=port, debug=True)
