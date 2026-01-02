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
    # print(response.text)
    return json.loads(response.text)

def create_data(list_id):
    cards = get_cards(list_id)
    dates = []
    for card in cards:
        # print(card)
        # break
        dt = card["dateLastActivity"]
        # dt = get_card_actions(card["id"])[0]["date"]
        dates.append(datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple().tm_yday)
    
    a = [0 for i in range(366)]
    for i in dates:
        a[i] += 1
    data = [sum(a[:i+1]) for i in range(366)]
    return data

def get_d(d):
    data = []
    charts = d["charts"]
    for chart in charts:
        # Books
        target = [(chart["target"]/365) * x for x in range(1, 366)]
        # books52 = [(24/365) * x for x in range(1, 366)]
        list_id = chart["id"]
        read = create_data(list_id)
        data.append({
            "name": chart["name"],
            "id": list_id,
            "datasets": [
                {"label": "Total",
                "data": read},
                {"label": chart["name"],
                "data": target},
                #  {
                #  "label": "24 Books",
                #  "data": books52,
                #  }
            ]
        })
    return data

def get_data():
    data = []

    # Books
    books36 = [(12/365) * x for x in range(1, 366)]
    # books52 = [(24/365) * x for x in range(1, 366)]
    list_id = "5fea6044ad7f3a3ee01bb25c"
    read = create_data(list_id)
    data.append({
        "name": "Books",
        "id": list_id,
        "datasets": [
            {"label": "Read",
             "data": read},
            {"label": "12 Books",
             "data": books36},
            #  {
            #  "label": "24 Books",
            #  "data": books52,
            #  }
        ]
    })

    # Papers
    papers = [(52/365) * x for x in range(1, 366)]
    list_id = "5fea603a0dc7f319c792a863"
    # list_id = "5be8de6f0a9807490540e6f2" # for testing
    read = create_data(list_id)
    data.append({
        "name": "52 Papers",
        "id": list_id,
        "datasets": [
            {"label": "Read",
             "data": read},
            {"label": "52 Papers",
             "data": papers},
        ]
    })

    # 72 Audiobooks
    audiobooks = [(52/365) * x for x in range(1, 366)]
    list_id = "5feb639db0229c3a76f7c0de"
    read = create_data(list_id)
    data.append({
        "name": "Audio Books",
        "id": list_id,
        "datasets": [
            {"label": "Read",
             "data": read},
            {"label": "52 Audio Books",
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

    # 3 Textbooks
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

        print(response.text)

        data = json.loads(response.text)

        if sum(l["datasets"][0]["data"]) != len(data):
            refresh = True
            break

        # for i, d in enumerate(previous_data):
        #     if len(data[i]["datasets"][0]) != len(d["datasets"][0]):
        #         refresh = True

    return refresh



# @app.route('/')
# def home():
#     data = get_data()
#     # refresh = False
#     # try:
#     #     data = pickle.load(open("data.p", "rb"))
#     #     refresh = check_for_changes(data)
#     # except (OSError, IOError) as e:
#     #     data = get_data()
#     #     pickle.dump(data, open("data.p", "wb"))

#     # if refresh:
#     #     data = get_data()
#     #     pickle.dump(data, open("data.p", "wb"))


#     return render_template('index.html', data=data)#json.dumps([[1,2], [3,4]]))

@app.route('/2021')
def twentyone():
    d = {
        "id": "",
        "charts": [
            {
                "name": "Books",
                "id": "5fea6044ad7f3a3ee01bb25c",
                "target": 12,
            },
            {
                "name": "Papers",
                "id": "5fea603a0dc7f319c792a863",
                "target": 52,
            },
            {
                "name": "Audiobooks",
                "id": "5feb639db0229c3a76f7c0de",
                "target": 52,
            },
            {
                "name": "Courses",
                "id": "5fea603c103d0e777132f2a5",
                "target": 12,
            },
            {
                "name": "Textbooks",
                "id": "5fea6042d07ce105efef7b0d",
                "target": 4,
            },

        ],
    }
    data = get_d(d)
    return render_template('index.html', data=data)#json.dumps([[1,2], [3,4]]))

@app.route('/2023')
def twentythree():
    d = {
        "id": "",
        "charts": [
            {
                "name": "Books",
                "id": "63a6222dfd8cf601b752b210",
                "target": 12,
            },
            {
                "name": "Papers",
                "id": "63a6222dfd8cf601b752b20d",
                "target": 52,
            },
            {
                "name": "Audiobooks",
                "id": "63a6222dfd8cf601b752b212",
                "target": 52,
            },
            {
                "name": "Courses",
                "id": "63a6222dfd8cf601b752b20e",
                "target": 12,
            },
            {
                "name": "Textbooks",
                "id": "63a6222dfd8cf601b752b20f",
                "target": 4,
            },
            {
                "name": "Technical Books",
                "id": "63a6222dfd8cf601b752b211",
                "target": 4,
            },
            # {
            #     "name": "Talks",
            #     "id": "63a72fa7792d3300b3e0eb35",
            #     "target": 50,
            # },
            {
                "name": "Algorithms",
                "id": "63b0dd5400f25e00c27e3879",
                "target": 26,
            },

        ],
    }
    data = get_d(d)
    return render_template('index.html', data=data)#json.dumps([[1,2], [3,4]]))

@app.route('/2024')
def twentyfour():
    d = {
        "id": "",
        "charts": [
            {
                "name": "Books",
                "id": "6580d1360485c451ef012c68",
                "target": 12,
            },
            {
                "name": "Papers",
                "id": "6768c05183f146b395a76559",
                "target": 70,
            },
            {
                "name": "Audiobooks",
                "id": "6580d1360485c451ef012c6a",
                "target": 52,
            },
            {
                "name": "Courses",
                "id": "6580d1360485c451ef012c66",
                "target": 10,
            },
            {
                "name": "Textbooks",
                "id": "6580d1360485c451ef012c67",
                "target": 3,
            },
            # {
            #     "name": "Technical Books",
            #     "id": "6580d1360485c451ef012c69",
            #     "target": 4,
            # },
            # {
            #     "name": "Talks",
            #     "id": "63a72fa7792d3300b3e0eb35",
            #     "target": 50,
            # },
            {
                "name": "Algorithms/Tutorials",
                "id": "6580d1360485c451ef012c6c",
                "target": 26,
            },

        ],
    }
    data = get_d(d)
    return render_template('index.html', data=data)#json.dumps([[1,2], [3,4]]))

@app.route('/2025')
def twentyfive():
    d = {
        "id": "",
        "charts": [
            {
                "name": "Books",
                "id": "6768c05183f146b395a7655d",
                "target": 12,
            },
            {
                "name": "Papers",
                "id": "6768c05183f146b395a7655a",
                "target": 70,
            },
            {
                "name": "Audiobooks",
                "id": "6768c05183f146b395a7655f",
                "target": 48,
            },
            {
                "name": "Courses",
                "id": "6768c05183f146b395a7655b",
                "target": 10,
            },
            {
                "name": "Textbooks",
                "id": "6768c05183f146b395a7655c",
                "target": 3,
            },
            # {
            #     "name": "Technical Books",
            #     "id": "6580d1360485c451ef012c69",
            #     "target": 4,
            # },
            # {
            #     "name": "Talks",
            #     "id": "63a72fa7792d3300b3e0eb35",
            #     "target": 50,
            # },
            {
                "name": "Algorithms/Tutorials",
                "id": "6768c05183f146b395a76561",
                "target": 26,
            },

        ],
    }
    data = get_d(d)
    return render_template('index.html', data=data)#json.dumps([[1,2], [3,4]]))

@app.route('/')
def home():
    d = {
        "id": "",
        "charts": [
            {
                "name": "Books",
                "id": "694b4a8b74675ea759b79ece",
                "target": 6,
            },
            {
                "name": "Papers",
                "id": "694b4a8b74675ea759b79ecb",
                "target": 100,
            },
            {
                "name": "Audiobooks",
                "id": "694b4a8b74675ea759b79ed0",
                "target": 36,
            },
            {
                "name": "Courses",
                "id": "694b4a8b74675ea759b79ecc",
                "target": 12,
            },
            {
                "name": "Textbooks",
                "id": "694b4a8b74675ea759b79ecd",
                "target": 2,
            },
            # {
            #     "name": "Technical Books",
            #     "id": "6580d1360485c451ef012c69",
            #     "target": 4,
            # },
            # {
            #     "name": "Talks",
            #     "id": "63a72fa7792d3300b3e0eb35",
            #     "target": 50,
            # },
            {
                "name": "Algorithms/Tutorials",
                "id": "694b4a8b74675ea759b79ed2",
                "target": 26,
            },

        ],
    }
    data = get_d(d)
    return render_template('index.html', data=data)#json.dumps([[1,2], [3,4]]))

if __name__ == '__main__':
    app.run(debug=True)