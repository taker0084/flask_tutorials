import pytest
from flask import g, session
from flaskr.db import get_db

#ユーザー登録のテスト
def test_register(client, app):
    assert client.get('/auth/register/').status_code == 200             #user登録画面('/auth/register')へアクセスができるか(statusが200か)
    response = client.post(
        '/auth/register/', data={'username': 'a', 'password': 'a'}      #username='a'、password='a'として登録
    )
    assert response.headers["Location"] == "/auth/login/"               #ログイン画面にリダイレクトされているか

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",                 #dbからusernameが'a'の人を抽出
        ).fetchone() is not None                                       #usernameが'a'の人が存在しているか

#user登録のバリデーションを確認
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),                                #両方空欄の場合,"Username is required"
    ('a', '', b'Password is required.'),                               #パスワードが空欄の場合、"Password is required"
    ('test', 'test', b'already registered'),                           #すでに登録されている場合、"already registered"
))
def test_register_validate_input(client, username, password, message):
    #上のパターンについてPostメソッドでアクセスしてみる
    response = client.post(
        '/auth/register/',
        data={'username': username, 'password': password}
    )
    assert message in response.data

#ユーザーログインのテスト
def test_login(client, auth):
    assert client.get('/auth/login/').status_code == 200                 #'/auth/login'へのアクセスがうまくいくか
    response = auth.login()
    assert response.headers["Location"] == "/"                          #ログインがうまくいけば、自動的に'/'にリダイレクト

    with client:
        client.get('/')
        assert session['user_id'] == 1                                  #ログインした際のsessionIDが1になっているか
        assert g.user['username'] == 'test'                             ##リクエストのuser名がtestになっているか


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

#ログアウト
def test_logout(client, auth):
    auth.login()                                                        #ログイン

    with client:
        auth.logout()                                                   #ログアウト
        assert 'user_id' not in session                                 #ログアウト後にセッションにuserIDが残っていないか