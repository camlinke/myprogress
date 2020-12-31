from flask import Flask
from flask import render_template
import json
import pickle
import requests
import datetime
import os

app = Flask(__name__)

key = os.environ["TRELLO_KEY"]
token = os.environ["TRELLO_TOKEN"]

def get_card_actions(card_id):
    card = card_id
    url = f"https://api.trello.com/1/cards/{card}/actions?filter=all"

    headers = {
       "Accept": "application/json"
    }

    query = {
       'key': key,
       'token': token,
    }

    response = requests.request(
       "GET",
       url,
       headers=headers,
       params=query
    )
    return json.loads(response.text)

def get_cards(list_id):
    url = f"https://api.trello.com/1/lists/{list_id}/cards"

    headers = {
       "Accept": "application/json"
    }

    query = {
       'key': key,
       'token': token,
    }

    response = requests.request(
       "GET",
       url,
       headers=headers,
       params=query
    )
    return json.loads(response.text)

def create_data(list_id):
    cards = get_cards(list_id)
    dates = []
    for card in cards:
        dt = get_card_actions(card["id"])[-1]["date"]
        dates.append(datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple().tm_yday)
    
    a = [0 for i in range(366)]
    for i in dates:
        a[i] += 1
    data = [sum(a[:i+1]) for i in range(366)]
    return data

def get_data():
    data = []

    # Books
    books36 = [(36/365) * x for x in range(1, 366)]
    books52 = [(52/365) * x for x in range(1, 366)]
    list_id = "5fea6044ad7f3a3ee01bb25c"
    read = create_data(list_id)
    data.append({
        "name": "Books",
        "id": list_id,
        "datasets": [
            {"label": "Read",
             "data": read},
            {"label": "36 Books",
             "data": books36},
             {
             "label": "52 Books",
             "data": books52,
             }
        ]
    })

    # Papers
    papers = [(100/365) * x for x in range(1, 366)]
    list_id = "5fea603a0dc7f319c792a863"
    # list_id = "5be8de6f0a9807490540e6f2" # for testing
    read = create_data(list_id)
    data.append({
        "name": "100 Papers",
        "id": list_id,
        "datasets": [
            {"label": "Read",
             "data": read},
            {"label": "100 Papers",
             "data": papers},
        ]
    })

    # 72 Audiobooks
    audiobooks = [(72/365) * x for x in range(1, 366)]
    list_id = "5feb639db0229c3a76f7c0de"
    read = create_data(list_id)
    data.append({
        "name": "Audio Books",
        "id": list_id,
        "datasets": [
            {"label": "Read",
             "data": read},
            {"label": "72 Audio Books",
             "data": audiobooks},
        ]
    })

    # Courses
    courses = [(8/365) * x for x in range(1, 366)]
    list_id = "5fea603c103d0e777132f2a5"
    read = create_data(list_id)
    data.append({
        "name": "Courses",
        "id": list_id,
        "datasets": [
            {"label": "Read",
             "data": read},
            {"label": "8 Courses",
             "data": courses},
        ]
    })

    # 6 Textbooks
    textbooks = [(6/365) * x for x in range(1, 366)]
    list_id = "5fea6042d07ce105efef7b0d"
    read = create_data(list_id)
    data.append({
        "name": "Textbooks",
        "id": list_id,
        "datasets": [
            {"label": "Read",
             "data": read},
            {"label": "6 Textbooks",
             "data": textbooks},
        ]
    })

    return data

def check_for_changes(previous_data):
    refresh = False

    for l in previous_data:
        list_id = l["id"]
        url = f"https://api.trello.com/1/lists/{list_id}/cards"

        headers = {
           "Accept": "application/json"
        }

        query = {
           'key': key,
           'token': token,
        }

        response = requests.request(
           "GET",
           url,
           headers=headers,
           params=query
        )

        data = json.loads(response.text)

        if sum(l["datasets"][0]["data"]) != len(data):
            refresh = True
            break

        # for i, d in enumerate(previous_data):
        #     if len(data[i]["datasets"][0]) != len(d["datasets"][0]):
        #         refresh = True

    return refresh



@app.route('/')
def home():
    refresh = False
    try:
        data = pickle.load(open("data.p", "rb"))
        refresh = check_for_changes(data)
    except (OSError, IOError) as e:
        data = get_data()
        pickle.dump(data, open("data.p", "wb"))

    if refresh:
        data = get_data()
        pickle.dump(data, open("data.p", "wb"))

    return render_template('index.html', data=data)#json.dumps([[1,2], [3,4]]))

if __name__ == '__main__':
    app.run(debug=True)