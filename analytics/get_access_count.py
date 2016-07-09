# coding: utf-8

from os import path
import json
import httplib2
from datetime import datetime, timedelta
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from mongo import MongoUtil

CONFIG_PATH = path.dirname(path.abspath(__file__)) +'/config/analytics_conf.json'
DB_NAME = 'db.name'
SERVICE_ACCOUNT_EMAIL = 'service.account.email'
SERVICE_ACCOUNT_SECRET = 'service.account.secret'
PROFILE_ID = 'profile.id'
SCOPES = 'scopes'

# 除外するURLパターン一覧
EXCLUDES = ['/', '/author/.*', '/page/.*', '/tag/.*']


def conf_loader():
    '''コンフィグを読み込んでJSONを返すローダー
    '''
    with open(CONFIG_PATH, 'r') as f:
        conf = json.load(f)
        return conf


def init_service(conf):
    '''コンフィグを読み込んで、GoogleAnalyticsのサービスを返す
    '''
    with open(conf[SERVICE_ACCOUNT_SECRET], 'r') as f:
        keydict = json.load(f)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(keydict, conf[SCOPES])
        http = httplib2.Http()
        http = credentials.authorize(http)
        return build('analytics', 'v3', http=http)


def main():
    conf = conf_loader()
    service = init_service(conf)
    today = datetime.now()
    a_week_ago = today - timedelta(days=6)
    # リクエスト結果
    res = service.data().ga().get(
        ids=conf[PROFILE_ID],
        start_date=a_week_ago.strftime('%Y-%m-%d'),
        end_date=today.strftime('%Y-%m-%d'),
        dimensions='ga:pagePath',
        filters='ga:pagePath!=' + ';ga:pagePath!~'.join(EXCLUDES),
        metrics='ga:pageviews',
        sort='-ga:pageviews',
    ).execute()
    res['query']['period'] = 'week'
    # DBへの登録
    col = MongoUtil().create_col(conf[DB_NAME], ['access_ranking'])
    col.update(
        {'query.period': 'week'},
        {'$set': res},
        upsert=True
    )


if __name__ == '__main__':
    main()
