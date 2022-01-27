from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from profile import User, select_email
import datetime
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient, DESCENDING

user_data = ''
client = MongoClient('mongodb+srv://test:passw0rd@qloak.05oow.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
chat_db = client.get_database('Qloak_chat_DB')
users_collection = chat_db.get_collection('users')
rooms_collection = chat_db.get_collection('rooms')
room_members_collection = chat_db.get_collection('room_members')
messages_collection = chat_db.get_collection("messages")

# user information list
user_information = []
# 0 : username
# 1 : email
# 2 : password | remember to hash first

def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id':username, 'email':email, 'password':password_hash})


def update_user(username, email, password):
    user_information[0] = username
    user_information[1] = email
    user_information[2] = password
    users_collection.update_many({'_id': username}, {'$set': {'email': email, 'password': password}})

def get_user(email):
    user_data = select_email(email)
    return User(user_data[0],user_data[1],user_data[2]) if user_data else None

def get_user_data(username):
    user_data = users_collection.find_one({'_id':username})
    return user_data

def get_room(room_id):
    return rooms_collection.find_one({'_id': ObjectId(room_id)})

def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one({'name': room_name, 'created_by': created_by, 'created_at': datetime.now()}).inserted_id
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
    return room_id

def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
    room_members_collection.insert_one(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
         'added_at': datetime.now(), 'is_room_admin': is_room_admin})

def update_room(room_id, room_name):
    rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    room_members_collection.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': room_name}})

def add_room_members(room_id, room_name, usernames, added_by):
    room_members_collection.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
          'added_at': datetime.now(), 'is_room_admin': False} for username in usernames])

def remove_room_members(room_id, usernames):
    room_members_collection.delete_many(
        {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})


def get_room_members(room_id):
    return list(room_members_collection.find({'_id.room_id': ObjectId(room_id)}))


def get_rooms_for_user(username):
    return list(room_members_collection.find({'_id.username': username}))


def is_room_member(room_id, username):
    return room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})


def is_room_admin(room_id, username):
    return room_members_collection.count_documents(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})


def save_message(room_id, text, sender):
    messages_collection.insert_one({'room_id': room_id, 'text': text, 'sender': sender, 'created_at': datetime.now()})


MESSAGE_FETCH_LIMIT = 3


def get_messages(room_id, page=0):
    offset = page * MESSAGE_FETCH_LIMIT
    messages = list(
        messages_collection.find({'room_id': room_id}).sort('_id', DESCENDING).limit(MESSAGE_FETCH_LIMIT).skip(offset))
    for message in messages:
        message['created_at'] = message['created_at'].strftime("%d %b, %H:%M")
    return messages[::-1]

#
# username = 'jacje'
#
# print(get_user(username).get_id())
# print(get_user_data(username)['email'])
# print(get_user(username).password)
# save_user('jacje','jacje@gmail.com','test')
# save_user('admin','adminguy@gmail.com','safepassword')