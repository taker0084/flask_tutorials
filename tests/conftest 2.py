import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

#data.sqlの内容をバイナリーモードで読み込んで
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    #utf-8エンコーディングでデコード
    _data_sql = f.read().decode('utf8')

#テストのための準備を行う
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()          #一時的なファイルを作成し、記述子とパスを取得

    app = create_app({                  #アプリケーションのインスタンスを生成
        'TESTING': True,                                   #テストモードをオン
        'DATABASE': db_path,                               #DBのパスを指定
    })

    with app.app_context():                                #gやcurrent_appなどのオブジェクトを使用可能
        init_db()
        get_db().executescript(_data_sql)                  #data.sqlの処理を実行

    yield app                                              #アプリケーションインスタンスをtestに渡す

    os.close(db_fd)                                     #一時的に作成したデータベースファイルとの接続を解除する
    os.unlink(db_path)                                #一時的に作成したDBファイルを削除


@pytest.fixture
def client(app):
    return app.test_client()                               #アプリケーションへのリクエストを行う


@pytest.fixture
def runner(app):
    return app.test_cli_runner()                           #アプリケーションの実行者


class AuthActions(object):                                 #認証を行うクラス
    def __init__(self, client):
        self._client = client                         #クライアントを引数として渡す

    def login(self, username='test', password='test'):
        return self._client.post(                          #クライアントが'/auth/login'にpostメソッドでアクセス → ログインできるか
            '/auth/login/',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout/')            #ログアウト画面にアクセス

@pytest.fixture
def auth(client):
    return AuthActions(client)