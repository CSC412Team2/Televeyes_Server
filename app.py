import requests
import json
from pymongo import MongoClient
from pymongo import errors
import utils
import datetime

client = MongoClient('mongodb://heroku_7plvr14k:ssqu1unoucs4diblm9n1p81p1u@ds139448.mlab.com:39448/heroku_7plvr14k')
db = client.get_default_database()
shows = db.shows
shows.create_index('id', unique = True)
shows.create_index([
        ("ngrams", "text"),
    ],
    name="search_show_ngrams",
    weights={
        "ngrams": 100
    }, language_override = 'dummy')

episodes = db.episodes
episodes.create_index('id', unique = True)

tvmaze = "http://api.tvmaze.com"
showUrl = tvmaze + "/shows"
episodeUrl = tvmaze + "/shows/id/episodes"

def getEpisodes(show):
    print(show)
    url = episodeUrl.replace('id', str(show))
    req = requests.get(url)
    parseEpisodes(req)

def getNextPage(num, func):
    url = showUrl + "?page=" + str(num)
    req = requests.get(url)
    func(req)

    if req.status_code != 404:
        getNextPage(num + 1, func)

def parseEpisodes(resp):
    j = json.loads(resp.text)
    try:
        episodes.insert(j)
    except errors.DuplicateKeyError:
        pass
    except errors.InvalidOperation:
        pass

def parseShows(resp):
    j = json.loads(resp.text)
    try:
        shows.insert_many(j, ordered=False)
    except errors.BulkWriteError as e:
        for i, item in enumerate(e.details['writeErrors']):
            del j[i]['_id']
            shows.update({'id' : j[i]['id']}, j[i])

    for i in j:
        utils.index_for_search(shows, i)
        if i['premiered'] != None:
            shows.update({'premiered': i['premiered']}, {'$set' : {'premiered' : datetime.datetime.strptime(i['premiered'], "%Y-%m-%d")}})
        getEpisodes(i['id'])

getNextPage(1, parseShows)