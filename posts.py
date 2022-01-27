import sqlite3
import os


def create_postdb(postid, imagepath, username, likecount, caption, postdate, posttime):
    conn = sqlite3.connect("userpost.db")
    # create cursor
    c = conn.cursor()
    # create table
    c.execute("""CREATE TABLE IF NOT EXISTS postdb(
        postid text,
        imagepath text,
        username text,
        likecount int, 
        caption text,
        postdate text,
        posttime text
        
    )""")
    c.execute("""INSERT INTO postdb (postid, imagepath, username, likecount, caption, postdate, posttime) VALUES(?, ?, ?, ?, ?, ?, ?)""",
              (postid, imagepath, username, likecount, caption, postdate, posttime)
              )
    conn.commit()
    conn.close()


def select(postid):
    result = []
    conn = sqlite3.connect("userpost.db")
    # create cursor
    c = conn.cursor()
    # create table
    c.execute("""SELECT * FROM postdb WHERE postid=?""", (postid,))
    row = c.fetchall()[0]
    for i in range(0, len(row)):
        result.append(row[i])
    conn.close()
    return result


def select_post_id():
    result = []
    conn = sqlite3.connect("userpost.db")
    # create cursor
    c = conn.cursor()
    # create table
    c.execute("""SELECT postid FROM postdb""")
    row = c.fetchall()
    for i in range(0, len(row)):
        result.append(row[i])
    conn.close()
    return result

def select_file_path(postid):
    result = []
    conn = sqlite3.connect("userpost.db")
    # create cursor
    c = conn.cursor()
    # create table
    c.execute("""SELECT imagepath FROM postdb WHERE postid=?""", (postid,))
    row = c.fetchall()[0]
    for i in range(0, len(row)):
        result.append(row[i])
    conn.close()
    return result





