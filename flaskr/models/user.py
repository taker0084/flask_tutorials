
from tkinter import NO
from flaskr.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash

class user:
  db=get_db()
  
  @classmethod
  def register(cls, username, password):
    error = None
    try:
      cls.db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",   #プレースホルダーによるSQLインジェクション対策
        (username, generate_password_hash(password)),   #パスワードのハッシュ化を行ってから保存
      )
      cls.db.commit()
    except cls.db.IntegrityError:
      error = f"User {username} is already registered."       #usernameは一意であるため、登録済みの場合エラーを表示
    
    return error
  
  @classmethod
  def get_by_name(cls,username):
    return cls.db.execute(
      'SELECT * FROM user WHERE username = ?', (username,)             #dbからusernameが一致する行を取得
    ).fetchone()  
  
  @classmethod
  def get_by_id(cls,user_id):
    return cls.db.execute(                             
      'SELECT * FROM user WHERE id = ?', (user_id,)                   #dbからidの一致する行を取得
    ).fetchone()