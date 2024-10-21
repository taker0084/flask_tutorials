import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()                                           #dbの接続と新たに接続を行った場合(get_db())の結果が同じか確認

    #データベースへの接続はここで切れる(db.pyに書いた38行目　teardown参照)
    with pytest.raises(sqlite3.ProgrammingError) as e: 
        db.execute('SELECT 1')                                          #接続が切れているDBに接続しようとする

    assert 'closed' in str(e.value)                              #エラーメッセージに'closed'が含まれているか確認

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):                                             #データベース初期化処理が呼び出されたかのみを記録するclass
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)              #testではinit_dbの代わりにfake_init_dbを行う
    result = runner.invoke(args=['init-db'])                       #コマンドラインで'init-db'を行う(実際の'flask init-db'に該当)
    assert 'Initialized' in result.output                               #コマンド成功メッセージが表示されるか確認
    assert Recorder.called                                              #内部的に初期化を行っているか確認