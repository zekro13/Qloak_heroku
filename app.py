import socket
from pymongo.errors import DuplicateKeyError
from jinja2 import *
from flask import Flask, render_template, redirect, url_for, request, session, Response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from eventlet import *
from chat import *
from datetime import datetime
from bson.json_util import dumps
from wtforms import *
from flask_wtf import *
import profile, posts
from werkzeug.utils import secure_filename
import os, random, string
from PIL import Image
import json, base64
from flask_sessions import Session
import matplotlib.pyplot as plt
import keras_ocr
from chat import get_user
from flask import Flask, render_template, redirect, url_for, session, request, logging
import profile
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from passlib.hash import sha256_crypt, argon2, bcrypt
from functools import wraps
# from flask_uploads import UploadSet, configure_uploads, IMAGES
import timeit
import datetime
from flask_mail import Mail, Message
import os
from wtforms.fields import EmailField
import sqlite3

app = Flask(__name__)
app.secret_key = 'super duper secret'
app.config['SECRET_KEY'] = 'super duper secret'
app.config["RECAPTCHA_PUBLIC_KEY"] = '6LeMUqodAAAAAJPlWbAlVj8kXJ8g53ljvGaO0-ZF'
app.config["RECAPTCHA_PRIVATE_KEY"] =   '6LeMUqodAAAAAACtSRulRjZs4XbjjeFM2uS_EoiR'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class Widgets(FlaskForm):
    recaptcha = RecaptchaField()

UPLOAD_FOLDER = '\images'
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_usernames():
    usernames = profile.select_usernames()
    print('usernames =', usernames)
    return usernames


@app.route('/')
def home():

    # username = 'usernameman'
    # password = 'password'
    # profile.create_user(username, password)
    # userobject = profile.user_profile(username, password)
    # session['user'] = userobject
    return render_template('author.html')


@app.route('/create')
def create():
    # for i in os.listdir('static/posts/images'):
    #     # username = ''.join(random.choice(string.ascii_letters) for i in range(10))
    #     name, extension = os.path.splitext(i)
    #     # os.rename('static/posts/images/'+i, f'static/posts/images/{username}1{extension}')
    #     username = name
    #     posts.create_postdb(username+'1',
    #                         f'static/posts/images/{username}{extension}',
    #                         username, random.randint(1,100),
    #                         f"hey this is {username}",
    #                         str(random.randint(1,30))+'/'+str(random.randint(1,12))+'/'+'20'+str(random.randint(0,9))+str(random.randint(0,9)),
    #                         str(random.randint(0,24)) + str(random.randint(0, 60))
    #                         )
    #     print(i)

    # for i in os.listdir('static/posts/images'):
    #     name, extension = os.path.splitext(i)
    #     username = name[:-1]
    #     password = 'password'
    #     profile.create_user(username, password)
    #     print(i)


    # table = posts.select_post_id()
    # print(table)

    # userobject = session['user']
    # attributes = userobject.select('username')
    # print(attributes)
    # return render_template('author.html')

    return render_template('author.html')


@app.route('/posting', methods=['GET', "POST"])
def posting():
    if request.method == "POST":
        file = request.files['image']
        if file and allowed_file(file.filename):
            if request.form['action'] == 'check image':
                filename = secure_filename(file.filename)
                height = int(request.form['height'])
                width = int(request.form['width'])

                file.save(os.path.join('static/temp/original/', filename))
                file = Image.open('static/temp/original/'+filename)
                file = file.resize((width, height))
                file.save('static/temp/'+filename)

                print('file uploaded')

                pipeline = keras_ocr.pipeline.Pipeline()

                # Get a set of three example images
                images = [
                    keras_ocr.tools.read(url) for url in [
                        'static/temp/'+filename
                    ]
                ]

                prediction_groups = pipeline.recognize(images)

                # Plot the predictions
                fig, axs = plt.subplots(nrows=len(images), figsize=(20, 20))

                try:
                    zipped = zip(axs, images, prediction_groups)
                except:
                    axs = [axs]
                    zipped = zip(axs, images, prediction_groups)

                for ax, image, predictions in zipped:
                    keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
                figpath = 'static/temp/figure/'+filename
                original = 'static/temp/original/'+filename
                plt.savefig(figpath)


                return render_template('posting.html', figpath=figpath, original=original, display='block')
            elif request.form['action'] == "submit":
                print('submit')
                return render_template('contact.html')
        print('tryagain')
        return render_template('posting.html')
    return render_template('posting.html', display='none')


@app.route('/register', methods=['GET', 'POST'])
# @not_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        # password_hash_test = sha256_crypt.hash(str(form.password.data))
        # print ("sha256 test hash: ", password_hash_test)
        password_hash_pass_a = argon2.using(rounds=5, salt=bytes(22)).hash(str(form.password.data))
        password_hash_pass_b = bcrypt.using(rounds=5, salt="GhvMmNVjRW29ulnudl.Lbu").hash(str(password_hash_pass_a))
        print ("bcrypt pass b: ", password_hash_pass_b)
        
        password_hash_final = password_hash_pass_b
        print("final password hash: ", password_hash_final)
        email = form.email.data
        mobile = form.mobile.data

        #test
        # print(username)
        # print(password)
        # print(email)
        # print(mobile)

        # Create Cursor
        conn = sqlite3.connect('userprofile.db')
        # cur = sqlite3.connection.cursor()
        conn.execute("INSERT INTO userprofiledb(username, password, email, mobile) VALUES(?, ?, ?, ?)",
                      (username, password_hash_final, email, mobile))

        # Commit cursor
        conn.commit()

        # Close Connection
        conn.close()

        # flash('You are now registered and can login', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# @app.route('/test_register_results')
# def test_register_results():
#     conn = sqlite3.connect('userprofile.db')
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM userprofiledb WHERE username=?", ("test",))
#     row = cur.fetchall()
#     result_list = row
#
#     print(row)
#     # print(result_list[0])
#
#     tup = result_list[0]
#     username = tup[0]
#     password = tup[1]
#     email = tup[2]
#     mobile = tup[3]
#
#     return render_template('test_register_results.html', username=username, password=password, email=email, mobile=mobile)


class RegisterForm(Form):
    username = StringField('', [validators.length(min=3, max=25)], render_kw={'placeholder': 'Username'})
    password = PasswordField('', [validators.length(min=3)],
                       render_kw={'placeholder': 'Password'})
    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    mobile = StringField('', [validators.length(min=8, max=15)], render_kw={'placeholder': 'Mobile'})\


@app.route('/get_posts')
def get_posts():
    # try:
    #     listofposts = session['listofposts']
    # except Exception as e:
    #     print(e)
    #     listofposts = posts.select_post_id()
    #     print('new')
    listofposts = posts.select_post_id()
    postid = listofposts[random.randint(0, len(listofposts))]
    # print(postid)
    # listofposts.remove(postid)
    # session['listofposts'] = listofposts
    # print(session['listofposts'])
    # print('updated session')
    processedpostid = postid[0]
    filepath = posts.select_file_path(processedpostid)
    details = posts.select(processedpostid)
    print(details)
    postid, imagepath, username, likecount, caption, postdate, posttime = details
    json_data = {'postid': postid, 'username': username, 'imagepath': imagepath, 'likecount': likecount, 'caption': caption, 'postdate': postdate, 'posttime': posttime}
    data = json.dumps(json_data)
    d = json.loads(data)
    return d


@app.route('/checkimage/<width>/<height>/<filename>')
def checkimage(width, height, filename):

    pipeline = keras_ocr.pipeline.Pipeline()

    # Get a set of three example images
    images = [
        keras_ocr.tools.read(pic) for pic in [
            'some.jpeg',
            'boug.jpeg'
        ]
    ]

    username = session['username']
    usernamelist = get_usernames()
    # Each list of predictions in prediction_groups is a list of
    # (word, box) tuples.
    prediction_groups = pipeline.recognize(images)

    # Plot the predictions
    fig, axs = plt.subplots(nrows=len(images), figsize=(20, 20))

    try:
        zipped = zip(axs, images, prediction_groups)
    except:
        axs = [axs]
        zipped = zip(axs, images, prediction_groups)

    for ax, image, predictions in zipped:
        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)

    plt.show()
    plt.savefig('static/temp/figure/'+'hi')

    return render_template('posting.html')


@app.route('/login' , methods=['GET','POST'])
def login():
        msg = ""
        if (request.method == 'POST'):
            email = request.form["email"]
            password = request.form["password"]

            password_hash_pass_a = argon2.using(rounds=5, salt=bytes(22)).hash(str(password))
            password_hash_pass_b = bcrypt.using(rounds=5, salt="GhvMmNVjRW29ulnudl.Lbu").hash(str(password_hash_pass_a))
            final_password_hashed = password_hash_pass_b


            print(final_password_hashed)
            # r = profile.login(email, password)
            r = profile.login(email, final_password_hashed)
            user = get_user(email)

            print(r)
            for i in r:
                print(i[2], i[1])
                # if (email == i[2], password == i[1]):

                if (email == i[2], final_password_hashed == i[1]):

                    login_user(user)
                    print('---------------------------')
                    print(current_user.username)
                    print('---------------------------')
                    return render_template('author.html')
                else:
                    msg = "Please enter valid email and password"
        return render_template("login.html", msg = msg)




@app.route('/logout' , methods=['GET','POST'])
#@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/Adminpage')
#@login_required
def adminpage():
    accountdict = {
        "2053D": {
            "Fname": "John",
            "Lname": "Smith",
            "Email": "johnsmith@gmail.com",
            "Password": "password123",
            "BirthDate": "12/07/2001",
            "Account_type": "user",
            "Status" : "online"
        },
        "20423D": {
            "Fname": "Jack",
            "Lname": "Tan",
            "Email": "jacktan@gmail.com",
            "Password": "password456",
            "BirthDate": "22/03/1984",
            "Account_type": "user",
            "Status": "online"
        },
        "3223D": {
            "Fname": "admin",
            "Lname": "guy",
            "Email": "adminguy@gmail.com",
            "Password": "safepassword",
            "BirthDate": "01/01/0101",
            "Account_type": "admin",
            "Status": "online"
        }
    }
    return render_template('Adminpage.html',
                           accountdict=accountdict)


@app.route('/messageroom')
#@login_required
def chat():
    rooms = []
    if current_user.is_authenticated:
        rooms = get_rooms_for_user(current_user.username)
    return render_template("chat.html", rooms=rooms, username=current_user.username)


@app.route('/create_room', methods = ['GET','POST'])
#@login_required
def create_room():
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        usernames = [username.strip() for username in request.form.get('members').split(',')]
        if len(room_name) and len(usernames):
            room_id = save_room(room_name, current_user.username)
            if current_user.username in usernames:
                usernames.remove(current_user.username)
            add_room_members(room_id, room_name, usernames, current_user.username)
            return redirect(url_for('view_room', room_id=room_id))
        else:
            message = "Failed to create room"
    return render_template('createroom.html')


@app.route('/rooms/<room_id>/')
#@login_required
def view_room(room_id):
    room = get_room(room_id)
    if room and is_room_member(room_id, current_user.username):
        room_members = get_room_members(room_id)
        messages = get_messages(room_id)
        return render_template('view_room.html', username=current_user.username, room=room, room_members=room_members,
                               messages=messages)
    else:
        return "Room not found", 404


@app.route('/rooms/<room_id>/messages/')
#@login_required
def get_older_messages(room_id):
    room = get_room(room_id)
    if room and is_room_member(room_id, current_user.username):
        page = int(request.args.get('page', 0))
        messages = get_messages(room_id, page)
        return dumps(messages)
    else:
        return "Room not found", 404


@app.route('/rooms/<room_id>/edit', methods=['GET', 'POST'])
#@login_required
def edit_room(room_id):
    room = get_room(room_id)
    if room and is_room_admin(room_id, current_user.username):
        existing_room_members = [member['_id']['username'] for member in get_room_members(room_id)]
        room_members_str = ",".join(existing_room_members)
        message = ''
        if request.method == 'POST':
            room_name = request.form.get('room_name')
            room['name'] = room_name
            update_room(room_id, room_name)

            new_members = [username.strip() for username in request.form.get('members').split(',')]
            members_to_add = list(set(new_members) - set(existing_room_members))
            members_to_remove = list(set(existing_room_members) - set(new_members))
            if len(members_to_add):
                add_room_members(room_id, room_name, members_to_add, current_user.username)
            if len(members_to_remove):
                remove_room_members(room_id, members_to_remove)
            message = 'Room edited successfully'
            room_members_str = ",".join(new_members)
        return render_template('edit_room.html', room=room, room_members_str=room_members_str, message=message)
    else:
        return "Room not found", 404


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],data['room'],data['message']))
    save_message(data['room'], data['message'], data['username'])
    data['created_at'] = datetime.now().strftime("%d %b, %H:%M")
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data)

@login_manager.user_loader
def load_user(email):
    return get_user(email)


if __name__ == "__main__":
    socketio.run(app, debug="true")

