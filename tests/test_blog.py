import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data                     #ログインのリンクが存在するか
    assert b"Register" in response.data                   #登録リンクが存在するか

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data                    #ログアウトのリンクが存在するか
    assert b'test title' in response.data                 #blogへ投稿したテストデータの名前が存在するか
    assert b'by test on 2018-01-01' in response.data      #テストの投稿日が2018-01-01か
    assert b'test\nbody' in response.data                 #テストデータのbodyを確認
    assert b'href="/1/update/"' in response.data           #テストデータのupdateリンクが存在するか

@pytest.mark.parametrize('path', (                        #投稿、修正、削除を一気にテスト
    '/create/',
    '/1/update/',
    '/1/delete/',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login/"  #ログインしないで投稿しようとするとログインページにリダイレクトするか


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1') #投稿の作成者のID(author_id)を、1から2へと変更
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update/').status_code == 403           #user_idが異なると、投稿が編集できないことを試す
    assert client.post('/1/delete/').status_code == 403           #user_idが異なると、投稿が削除できないことを試す
    # current user doesn't see edit link
    assert b'href="/1/update/"' not in client.get('/').data       #投稿の一覧ページに投稿の編集リンクが存在しないか

#存在しない投稿への編・削除ができないか確認
@pytest.mark.parametrize('path', (
    '/2/update/',
    '/2/delete/',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404                  #存在しない投稿へのアクセスには、Not Found

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create/').status_code == 200
    client.post('/create/', data={'title': 'created', 'body': ''})#本文なしで投稿を作成(titleはcreated)

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2                                        #投稿数が2つであるか確認(data.sql,上で作ったcreated)


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update/').status_code == 200
    client.post('/1/update/', data={'title': 'updated', 'body': ''}) #タイトルをupdatedに変更

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'                        #タイトルの変更が正しく反映されているか確認

#入力のバリデーションチェック
@pytest.mark.parametrize('path', (
    '/create/',
    '/1/update/',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data                #タイトル・本文両方とも空白の場合、エラーになるか

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete/')
    assert response.headers["Location"] == "/"                   #削除後に自動的に'/'にリダイレクトされるか

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None                                      #削除後に投稿が存在しないかチェック