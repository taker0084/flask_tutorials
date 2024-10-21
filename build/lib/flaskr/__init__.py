import os

from flask import Flask

# このファイルはApplication Factoryの関数


def create_app(test_config=None):
    # create and configure the app

    # Flaskインスタンスの作成,nameには実行したモジュール名(今回だとapp)が入る
    app = Flask(__name__, instance_relative_config=True)
    # __name__:モジュールとして呼び出されるとファイル名(他ファイルからインポートなど)、スクリプトとして実行されるとmainになる
    # instance_relative_config=True 設定ファイルがインスタンスフォルダから相対的に示される、インスタンスフォルダはflaskrの外側にできる

    app.config.from_mapping(  # 標準設定を行う
        SECRET_KEY="dev",  # データの安全性を保つために行う　→　本来は無作為な値で更新
        DATABASE=os.path.join(
            app.instance_path, "flaskr.sqlite"
        ),  # データベースへのパス、instance_pathはFlaskのインスタンスが存在
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile(
            "config.py", silent=True
        )  # もしインスタンスフォルダにconfig.pyがあれば標準設定を上書き
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)  # インスタンスフォルダを明示的に作成
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # dbへのアクセスをappインスタンスで使用可能にする
    from . import db

    db.init_app(app)

    # ログインとログアウトのviewへのアクセス
    from . import auth

    app.register_blueprint(auth.bp)

    # blog機能
    from . import blog

    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")  # blog.indexもindexも、両方同じURL'/'を参照する
    return app
