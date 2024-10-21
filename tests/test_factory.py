from flaskr import create_app


def test_config():
    #デフォルトのflaskrのテストフラグがFalseになっているか確認
    assert not create_app().testing
    #テストフラグをTrueにすると正しく反映されているかs
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    response = client.get('/hello')
    #'/hello'にアクセスした結果が'Hello World!'になっているか確認
    assert response.data == b'Hello, World!'