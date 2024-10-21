DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
/*userテーブルの定義*/
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT, /*IDはインクリメントで自動的に割り振られる*/
  username TEXT UNIQUE NOT NULL,        /*userNameは一意のテキストで、NULLではダメ*/
  password TEXT NOT NULL                /*passwordはテキストで、NULLはダメ*/
);
/*postテーブルの作成*/
CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,        /*postIDはインクリメントで自動的に割り振られる*/
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id) /*userテーブルへの外部キー*/
);