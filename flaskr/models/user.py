
from tkinter import NO

from flask import redirect, url_for
from flaskr.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash

class user:
  
  @classmethod
  def register(cls, username, password):
    error = None
    db=get_db()
    try:
      db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",   #プレースホルダーによるSQLインジェクション対策
        (username, generate_password_hash(password)),   #パスワードのハッシュ化を行ってから保存
      )
      db.commit()
    except db.IntegrityError:
      error = f"User {username} is already registered."       #usernameは一意であるため、登録済みの場合エラーを表示
    return error
  
  @classmethod
  def get_by_name(cls,username):
    db=get_db()
    error = None;
    if error is None:
      return db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)             #dbからusernameが一致する行を取得
      ).fetchone(),None  
    else: 
      return None,error
  
  @classmethod
  def get_by_id(cls,user_id):
    db=get_db()
    return db.execute(                             
      'SELECT * FROM user WHERE id = ?', (user_id,)                   #dbからidの一致する行を取得
    ).fetchone()