#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import re
import tempfile
import sqlite3
import uuid
from shogiimgsolver import ImageSolver
from flask import Flask, flash, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename

SQL_CREATE_TBL = """CREATE TABLE IF NOT EXISTS shogi (
    id TEXT NOT NULL PRIMARY KEY,
    result TEXT NULL,
    csa TEXT NULL,
    sfen TEXT NULL,
    image_name TEXT NULL,
    tsumi INTEGER
    );
"""
# 結果DB
DBNAME = "./shogi_sqlite3.db"


def execSql(sql):
    """SQLをsqliteで実行.SELECT文なら全データを返す"""
    result = None
    # スレッド毎に別のconnectionが必要なので毎回接続
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(sql)
    if sql.startswith("SELECT"):
        result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result


# 結果画像のディレクトリ
RESULTS_FOLDER = "./results"
# アップロードされる拡張子の制限
ALLOWED_EXT = set(["png", "jpg"])

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
# 最大4MBまでUpload可能に
app.config["MAX_CONTENT_LENGTH"] = 4 * 1000 * 1000

# 初期化
os.makedirs(RESULTS_FOLDER, exist_ok=True)
execSql(SQL_CREATE_TBL)
imageSolver = ImageSolver(options=[("USI_HASH", 128)])


@app.route("/", methods=["GET"])
def index():
    """indexページを表示"""
    return render_template("index.html")


@app.route("/", methods=["POST"])
def uploads_file():
    """ファイルをアップロードしたら、解析して次のページへ"""
    # ファイルがなかった場合の処理
    if "questimage" not in request.files:
        flash("ファイルがありません")
        return redirect(request.url)
    # データの取り出し
    file = request.files["questimage"]
    # ファイル名がなかった時の処理
    if not file or file.filename == "" or "." not in file.filename:
        flash("ファイルがありません")
        return redirect("/")
    if "." not in file.filename:
        flash("対応していないファイルです")
        return redirect("/")
    # ファイルのチェック
    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXT:
        flash("対応していないファイルです")
        return redirect("/")
    f = tempfile.NamedTemporaryFile(suffix="." + ext, delete=True)
    file.save(f.name)
    (result, sfen, csa, img) = imageSolver.solve_from_file(f.name)
    f.close()
    if result is None or sfen is None or img is None:
        flash("対応していないファイルです")
        return redirect("/")
    res_f = tempfile.NamedTemporaryFile(
        suffix="." + ext, dir=RESULTS_FOLDER, delete=False
    )
    img.save(res_f.name)
    res_f.close()
    # DBに結果を入れて、結果ページへリダイレクト。結果ページをbookmarkできるようにする
    id = str(uuid.uuid4()).replace("-", "")
    sql = (
        'INSERT INTO shogi(id, result, csa, sfen, image_name) values("%s", "%s", "%s", "%s", "%s");'
        % (id, result, csa, sfen, os.path.basename(res_f.name))
    )
    execSql(sql)
    return redirect("/shogi/" + id)


@app.route("/shogi/<id>")
def show_shogi(id):
    """結果ページを表示する"""
    # 英数以外の文字が入っていたらエラー
    matched = re.match(r"^[a-z0-9]+$", id)
    if not matched:
        return redirect("/")
    # SQLインジェクション対策: idは英数のみであることチェック済。
    sql = 'SELECT id, result, csa, sfen, image_name FROM shogi WHERE id="%s"' % id
    rows = execSql(sql)
    msg = {}
    for row in rows:
        msg["result"] = row[1]
        msg["sfen"] = row[3]
        msg["csa"] = row[2]
        msg["result_url"] = "/results/" + row[4]
    return render_template("result.html", message=msg)


@app.route("/results/<filename>")
def uploaded_file(filename):
    """画像ファイルを表示する"""
    if not filename or "." not in filename:
        return None
    # ファイルのチェック
    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXT:
        return None
    # 危険な文字を削除（サニタイズ処理）
    filename = secure_filename(filename)
    return send_from_directory(RESULTS_FOLDER, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
