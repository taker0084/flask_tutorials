from flaskr.db import get_db
from werkzeug.security import generate_password_hash

class post:
  
  @classmethod
  def showAll(cls):
    db = get_db()
    return db.execute(
        #DBから投稿のID、タイトル、内容、作成日時、投稿者のID、usernameを取得
        'SELECT p.id, title, body, created, author_id, username'
        #投稿者IDとuserIDを照会
        ' FROM post p JOIN user u ON p.author_id = u.id'
        #作成日時で降順に並べ、最新が一番上
        ' ORDER BY created DESC'
    ).fetchall()    
  
  @classmethod
  def save(cls,title,body,user_id):
    db = get_db()
    db.execute(
      'INSERT INTO post (title, body, author_id)'      #DBに行を挿入
      ' VALUES (?, ?, ?)',                             #SQLインジェクション対策
      (title,body,user_id)                      #タイトル、内容、ログインしているuserのID
    )
    db.commit()
    return None
  
  @classmethod
  def get(cls,post_id):
    db = get_db()
    return db.execute(                             
      'SELECT p.id, title, body, created, author_id, username'
      ' FROM post p JOIN user u ON p.author_id = u.id'
      #p.idが?(今回は変数id)と一致するものを取得
      ' WHERE p.id = ?',
      (post_id,)
    ).fetchone()

  @classmethod
  def update(cls,title,body,post_id):
    db = get_db()
    db.execute(
      #postテーブルのtitle、bodyに更新後の値を設定
      'UPDATE post SET title = ?, body = ?'
      ' WHERE id = ?',#更新する投稿のidを取得
      (title,body,post_id)
    )
    db.commit()
    return None

  @classmethod
  def delete(cls,id):
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return None