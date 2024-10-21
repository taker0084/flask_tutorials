import sqlite3

import click 

#gは特別なオブジェクトで、リクエストごとに異なる。複数の関数からアクセスするデータを格納
#current_appはリクエストを処理中のFaskアプリケーションを示す
from flask import current_app,g 

def init_db():
    db = get_db()                              #DBへのコネクションを取得

    with current_app.open_resource('schema.sql') as f:  #open_resourceだと相対パスでファイルを開ける
        db.executescript(f.read().decode('utf8'))
        
@click.command('init-db')                         #init-dbというコマンドを作成し、init_dbの処理を行う
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def get_db():
    if'db' not in g:
        g.db=sqlite3.connect(                          #データベースへのコネクションを作成、コネクションは同じリクエスト内で再利用
            current_app.config['DATABASE'],   #configが示すデータベースへ接続
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row                 #dictのように振る舞う行を返すようconnectionに伝える → 列名による列へのアクセス
        
    return g.db

def close_db(e=None):                                  #g.dbが設定されているかによってconnectionが作成されているか調査
    db=g.pop('db',None)
    
    if db is not None:                                 #g.dbが存在する場合、それを閉じる
        db.close()
        
def init_app(app):                                     #インスタンスに関数を登録
    app.teardown_appcontext(close_db)                  #レスポンス後のクリーンアップ中に処理を行う → リクエスト後にメモリなどを解放する(クリーンアップ)のと同時に、接続を解除
    app.cli.add_command(init_db_command)               #flaskコマンドで呼び出せるコマンドの追加(flask -app flaskr init_dbが使えるようになる)