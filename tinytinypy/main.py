#!/usr/bin/env python3

import http.client
import json
import xdg.BaseDirectory

class JsonClass:
    TRANS_EXP = {
        "same_key": True,
        "class_key": "json_key",
        "ignore_class_key": None,
    }
    @classmethod
    def getClassKey(cls, jsonKey):
        for key, val in cls.TRANS.items():
            if val == jsonKey or (key == jsonKey and val == True):
                return key
        return None
    @classmethod
    def getJsonKey(cls, classKey):
        val = cls.TRANS.get(classKey, None)
        return classKey if val == True else val
    @classmethod
    def fromJson(cls, dataDict):
        return cls(**{cls.getClassKey(key): val for key, val in dataDict.items() if cls.getClassKey(key) is not None and val is not None})
    def toJson(self):
        return {self.__class__.getJsonKey(key): val for key, val in self.__dict__.items() if self.__class__.getJsonKey(key) is not None and val is not None}

# Class Invalid
class TtRssCounters:
    def __init__(feeds=None, labels=None, categories=None, tags=None):
        self.feeds = feeds
        self.labels = labels
        self.categories = categories
        self.tags = tags

class Category(JsonClass):
    TRANS = {
        "catId": "id",
        "title": True,
        "unread": True,
        "orderId": "order_id",
    }
    def __init__(self, catId, title=None, unread=None, orderId=None):
        self.catId = catId
        self.title = title
        self.unread = unread
        self.orderId = orderId

class Feed(JsonClass):
    TRANS = {
        "feedId": "id",
        "title": True,
        "url": True,
        "catId": "cat_id",
        "unread": True,
        "lastUpdated": "last_updated",
        "orderId": "order_id",
    }
    def __init__(self, feedId, title=None, url=None, catId=None, unread=None, lastUpdated=None, orderId=None):
        self.feedId = feedId
        self.title = title
        self.url = url
        self.catId = catId
        self.unread = unread
        self.lastUpdated = lastUpdated
        self.orderId = orderId

class Headline(JsonClass):
    OLD_TRANS = { # TODO Add missing values to class
        "guid": None,
        "comments_count": None,
        "comments_link": None,
        "always_display_attachments": None,
        "note": None,
        "lang": None,
        "content": None,
        "flavor_image": None,
        "flavor_stream": None,
    }
    TRANS = {
        "headlineId": "id",
        "unread": True,
        "marked": True,
        "published": True,
        "updated": True,
        "isUpdated": "is_updated",
        "title": True,
        "url": "link",
        "feedId": "feed_id",
        "tags": True,
        "labels": True,
        "feedTitle": "feed_title",
        "author": True,
        "score": True,
    }
    def __init__(self, headlineId, unread, marked, published, updated, isUpdated, title, url, feedId, tags, labels, feedTitle, author, score):
        self.headlineId = headlineId
        self.unread = unread
        self.marked = marked
        self.published = published
        self.updated = updated
        self.isUpdated = isUpdated
        self.title = title
        self.url = url
        self.feedId = feedId
        self.tags = tags
        self.labels = labels
        self.feedTitle = feedTitle
        self.author = author
        self.score = score

class TtRssInstance:

    def __init__(self, host, endpoint="/api/"):
        self._host = host
        self._endpoint = endpoint
        self._sid = None
        self.__conn = http.client.HTTPSConnection(host)
        atexit.register(lambda: self.__conn.close())

    def __raiseError(self, op, info):
        if type(info) == 'dict':
            if 'error' not in info:
                if 'content' not in info:
                    raise Exception(f"Invalid info for error: {info}")
                info = info['content']
            err = info['error']
        else:
            err = info
        raise Exception(f"API Call {op} failed: {info['error']}")

    def _get(self, op, sendSid=True, **parameters):
        headers = {
                'Content-Type': 'application/json',
        }
        post_body = {k: v for k, v in parameters.items() if v is not None}
        post_body['op'] = op
        if sendSid:
            if self.__sid is None:
                raise Exception(f"Login required before API Call {op}")
            post_body['sid'] = self.__sid
        self.__conn.request('POST', self._endpoint, json.dumps(post_body), headers)
        res = self.__conn.getresponse()
        if res.status != 200:
            raise Exception(f"Return Code is {res.status} {res.reason}!")
        ret = json.loads(res.read().decode('utf8'))
        return ret

    def _getSafe(self, op, sendSid=True, **parameters):
        r = self._get(op, sendSid=sendSid, **parameters)
        if r['status'] != 0:
            if r['content']['error'] == 'NOT_LOGGED_IN':
                raise Exception(f"Authentication failed!")
            self.__raiseError(op, r)
        return r['content']

    def getApiLevel(self):
        r = self._get("getApiLevel")
        if r['status'] != 0:
            return 0 # Asume api level 0 on fail
        return r['content']['level']

    def getVersion(self):
        return self._getSafe("getVersion")['version']

    def login(self, username, password):
        r = self._get("login", sendSid=False, user=username, password=password)
        if r['status'] != 0:
            err = r['content']['error']
            if err == 'API_DISABLED':
                raise Exception(f"API disabled for user {username}")
            elif err == 'LOGIN_ERROR':
                raise Exception(f"Login failed for user {username}")
            else:
                self.__raiseError('login', err)
        self.__sid = r['content']['session_id']
        return True

    def logout(self):
        r = self._get("logout")
        if r['status'] != 0:
            err = r['content']['error']
            if err != 'NOT_LOGGED_IN':
                self.__raiseError('logout', err)
        self._sid = None
        return True

    def isLoggedIn(self):
        if self.__sid is None:
            return False
        r = self._get("isLoggedIn")
        if r['status'] != 0:
            err = r['content']['error']
            if err == 'NOT_LOGGED_IN':
                return False
            else:
                self.__raiseError('logout', err)
        return r['status']['content']['status']

    def getUnread(self):
        return int(self._getSafe("getUnread")['unread'])

    # TODO Broken
    def getCounters(self, feeds=True, labels=True, categories=True, tags=False):
        mode = ''
        if feeds:
            mode += 'f'
        if labels:
            mode += 'l'
        if categories:
            mode += 'c'
        if tags:
            mode += 't'
        r = self._getSafe("getCounters", output_mode=mode)
        #return TtRssCounters(r.get('feeds', None), r.get('labels', None), r.get('categories', None), r.get('tags', None))
        return r

    def getFeeds(self, cat_id=-3, unread_only=False, limit=None, offset=None, include_nested=False):
        r = self._getSafe("getFeeds", cat_id=cat_id, unread_only=unread_only, limit=limit, offset=offset, include_nested=include_nested)
        return [Feed.fromJson(data) for data in r]

    def getCategories(self, unread=False, nested=False, empty=True):
        r = self._getSafe('getCategories', unread_only=unread, enable_nested=nested, include_empty=empty)
        return [Category.fromJson(data) for data in r]

    def getHeadlines(self, feed_id=None, cat_id=None, limit=None, skip=None, show_excerpt=False, show_content=False, view_mode='all_articles', include_attachments=False, since_id=None, nested=None, order_by=None, sanitize=True, force_update=False, has_sandbox=False):
        is_cat = False
        send_feed_id = feed_id
        if cat_id is not None:
            if feed_id is not None:
                raise Exception("cat_id and feed_id cannot be set both!")
            is_cat = True
            send_feed_id = cat_id
        r = self._getSafe('getHeadlines', feed_id=send_feed_id, limit=limit, skip=skip, show_excerpt=show_excerpt, show_content=show_content, view_mode=view_mode, include_attachments=include_attachments, since_id=since_id, include_nested=nested, order_by=order_by, sanitize=sanitize, force_update=force_update, has_sandbox=has_sandbox)
        return [Headline.fromJson(data) for data in r]