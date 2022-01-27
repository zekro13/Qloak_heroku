from werkzeug.security import *
import sqlite3

class User:

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def is_authenticated(self):
        return True

    @staticmethod
    def is_active(self):
        return True

    @staticmethod
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def check_password(self,password_input):
        return check_password_hash(self.password, password_input)


def create_user(username, password):
    conn = sqlite3.connect("userprofile.db")
    #create cursor
    c = conn.cursor()
    #create table
    c.execute("""CREATE TABLE IF NOT EXISTS userprofiledb(
        username text,
        password text, 
        UNIQUE (username)
    )""")
    c.execute("""INSERT INTO userprofiledb (username, password) VALUES(?, ?)""", (username, password))
    conn.commit()
    conn.close()


def select(user):
    result = []
    conn = sqlite3.connect("userprofile.db")
    #create cursor
    c = conn.cursor()
    #create table
    c.execute("""SELECT username, password FROM userprofiledb WHERE username=?""", (user,))
    row = c.fetchall()[0]
    for i in range(0, len(row)):
        result.append(row[i])
    conn.close()
    return result


def select_usernames():
    result = []
    conn = sqlite3.connect("userprofile.db")
    #create cursor
    c = conn.cursor()
    #create table
    c.execute("""SELECT username FROM userprofiledb""")
    row = c.fetchall()[0]
    for i in range(0, len(row)):
        result.append(row[i])
    conn.close()
    return result

def select_email(email):
    try:
        result = []
        conn = sqlite3.connect("userprofile.db")
        #create cursor
        c = conn.cursor()
        #create table
        c.execute("""SELECT username, email, password FROM userprofiledb WHERE email=?""", (email,))
        row = c.fetchall()[0]
        print(row)
        for i in range(0, len(row)):
            result.append(row[i])
        conn.close()
        return result
    except IndexError:
        return None

def login(email, final_password_hashed):
    conn = sqlite3.connect("userprofile.db")
    c = conn.cursor()
    c.execute("""SELECT * FROM userprofiledb WHERE email = ? and password = ?""", (email, final_password_hashed))
    r = c.fetchall()
    return r

print(select_email('dsadsa'))