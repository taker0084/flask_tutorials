import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

#Blueprintはviewやコードをまとめる方法、今回は`auth`というグループを作成する
#`auth`グループ内の関数では全て前に/authがつく
bp = Blueprint('auth', __name__, url_prefix='/auth')

#サインアップ画面のview関数
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",   #プレースホルダーによるSQLインジェクション対策
                    (username, generate_password_hash(password)),   #パスワードのハッシュ化を行ってから保存
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."       #usernameは一意であるため、登録済みの場合エラーを表示
            else:
                return redirect(url_for("auth.login"))     #データを保存したらログイン画面に遷移,url_forは関数名からURLを生成

        flash(error)                                                 #エラーをセッションに保存し、レンダリングされた時にエラーをhtmlに組み込む

    return render_template('auth/register.html')       #テンプレートを使用

#ログイン画面のURL
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()                                      #DBへのコネクションを作成
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)             #dbからusernameが一致する行を取得
        ).fetchone()                                                         #クエリから一行のみ返す(特定のuserの情報は一行のみ)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):#入力されたパスワードのハッシュ値と、保存したハッシュ値を比較
            error = 'Incorrect password.'

        if error is None:
            session.clear()                                                  #ログインが成功した場合、セッションを初期化 → セッションはリクエストを跨いで格納されるデータのdict
            session['user_id'] = user['id']                                  #セッションにユーザーIDを登録
            return redirect(url_for('index'))              #初期画面に遷移

        flash(error)

    return render_template('auth/login.html')

#全てのview関数の前にuserがログイン済みかを確認
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:                                                                     #ログイン済みの場合、user情報をリクエストに付与
        g.user = get_db().execute(                             
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

#ログアウト処理       
@bp.route('/logout')
def logout():
    session.clear()                                                           #セッションを初期化し、ログイン情報を削除
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)                                            #元のview関数の処理を行う前に処理を行う
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))          #ログインしていない場合は自動的にログイン画面に遷移

        return view(**kwargs)                                                 #ログインしていれば元のview関数を実行

    return wrapped_view
