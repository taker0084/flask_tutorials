from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)  # 今回はblog機能がメインのため、url_prefix(`auth`のようなもの)は付けないようにしている

#投稿を全て表示
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        #DBから投稿のID、タイトル、内容、作成日時、投稿者のID、usernameを取得
        'SELECT p.id, title, body, created, author_id, username'
        #投稿者IDとuserIDを照会
        ' FROM post p JOIN user u ON p.author_id = u.id'
        #作成日時で降順に並べ、最新が一番上
        ' ORDER BY created DESC'
    ).fetchall()                                                 #クエリの結果を全て表示
    return render_template('blog/index.html', posts=posts)

#投稿を保存
@bp.route('/create', methods=('GET', 'POST'))
@login_required                                                  #ログインしているかを確認
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)                                 #エラーがあれば表示
        else:                                                    #なければDBに保存
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'      #DBに行を挿入
                ' VALUES (?, ?, ?)',                             #SQLインジェクション対策
                (title, body, g.user['id'])                      #タイトル、内容、ログインしているuserのID
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

#特定の投稿を取得
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        #p.idが?(今回は変数id)と一致するものを取得
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")         #404は、NotFoundエラー,　statusの後にエラーの文言を追加できる

    if check_author and post['author_id'] != g.user['id']:
        abort(403)                                         #403は、Forbidden(禁止)エラー

    return post

#投稿の編集
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                #postテーブルのtitle、bodyに更新後の値を設定
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',#更新する投稿のidを取得
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

#投稿の削除
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required                                                  #ログイン済みか確認
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))