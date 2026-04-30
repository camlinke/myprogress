from flask import Flask
from flask import render_template
import csv
import json
import pickle
import requests
import datetime
import os
from pathlib import Path

CACHE_FILE = "cache.csv"
CACHE_TTL_HOURS = 12

app = Flask(__name__)

key = os.environ["TRELLO_KEY"]
token = os.environ["TRELLO_TOKEN"]

@app.context_processor
def inject_year_context():
    today = datetime.date.today()
    return {
        "today_day": today.timetuple().tm_yday,
        "current_year": today.year,
    }

YEARS = {
    2021: {
        "Books":      "5fea6044ad7f3a3ee01bb25c",
        "Papers":     "5fea603a0dc7f319c792a863",
        "Audiobooks": "5feb639db0229c3a76f7c0de",
        "Courses":    "5fea603c103d0e777132f2a5",
    },
    2023: {
        "Books":      "63a6222dfd8cf601b752b210",
        "Papers":     "63a6222dfd8cf601b752b20d",
        "Audiobooks": "63a6222dfd8cf601b752b212",
        "Courses":    "63a6222dfd8cf601b752b20e",
    },
    2024: {
        "Books":      "6580d1360485c451ef012c68",
        "Papers":     "6768c05183f146b395a76559",
        "Audiobooks": "6580d1360485c451ef012c6a",
        "Courses":    "6580d1360485c451ef012c66",
    },
    2025: {
        "Books":      "6768c05183f146b395a7655d",
        "Papers":     "6768c05183f146b395a7655a",
        "Audiobooks": "6768c05183f146b395a7655f",
        "Courses":    "6768c05183f146b395a7655b",
    },
    2026: {
        "Books":      "694b4a8b74675ea759b79ece",
        "Papers":     "694b4a8b74675ea759b79ecb",
        "Audiobooks": "694b4a8b74675ea759b79ed0",
        "Courses":    "694b4a8b74675ea759b79ecc",
    },
}

COMPARE_CATEGORIES = ["Books", "Papers", "Audiobooks", "Courses"]

YEAR_COLORS = {
    2021: "#94a3b8",
    2023: "#3b82f6",
    2024: "#10b981",
    2025: "#f59e0b",
    2026: "#ec4899",
}

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
    try:
        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            params={'key': key, 'token': token},
            timeout=10,
        )
        response.raise_for_status()
        data = json.loads(response.text)
        if not isinstance(data, list):
            return None
        return data
    except (requests.RequestException, ValueError) as e:
        app.logger.warning("trello fetch failed for list %s: %s", list_id, e)
        return None

def read_cache(list_id, allow_stale=False):
    if not Path(CACHE_FILE).exists():
        return None
    with open(CACHE_FILE, newline='') as f:
        rows = [row for row in csv.DictReader(f) if row['list_id'] == list_id]
    if not rows:
        return None
    if not allow_stale:
        cached_at = datetime.datetime.fromisoformat(rows[0]['cached_at'])
        age = datetime.datetime.now(datetime.timezone.utc) - cached_at
        if age.total_seconds() > CACHE_TTL_HOURS * 3600:
            return None
    return [row['dateLastActivity'] for row in rows if row['dateLastActivity']]

def write_cache(list_id, dates):
    existing_rows = []
    if Path(CACHE_FILE).exists():
        with open(CACHE_FILE, newline='') as f:
            existing_rows = [row for row in csv.DictReader(f) if row['list_id'] != list_id]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    new_rows = [{'list_id': list_id, 'dateLastActivity': d, 'cached_at': now} for d in dates]
    with open(CACHE_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['list_id', 'dateLastActivity', 'cached_at'])
        writer.writeheader()
        writer.writerows(existing_rows + new_rows)

def create_data(list_id):
    dates = read_cache(list_id)
    if dates is None:
        cards = get_cards(list_id)
        if cards is not None:
            dates = [c["dateLastActivity"] for c in cards
                     if isinstance(c, dict) and c.get("dateLastActivity")]
            write_cache(list_id, dates)
        else:
            dates = read_cache(list_id, allow_stale=True) or []

    day_nums = [datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple().tm_yday for dt in dates]
    a = [0 for i in range(366)]
    for i in day_nums:
        a[i] += 1
    return [sum(a[:i+1]) for i in range(366)]

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
    return render_template('index.html', data=data, year=2021)

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
    return render_template('index.html', data=data, year=2023)

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
    return render_template('index.html', data=data, year=2024)

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
    return render_template('index.html', data=data, year=2025)

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
    return render_template('index.html', data=data, year=2026)

@app.route('/compare')
def compare():
    available_years = sorted(YEARS.keys())
    cards = []
    for category in COMPARE_CATEGORIES:
        datasets = []
        for y in available_years:
            list_id = YEARS[y].get(category)
            if not list_id:
                continue
            datasets.append({
                "label": str(y),
                "year": y,
                "color": YEAR_COLORS.get(y, "#64748b"),
                "data": create_data(list_id),
            })
        cards.append({"name": category, "datasets": datasets})
    return render_template(
        'compare.html',
        categories=cards,
        available_years=available_years,
        year_colors=YEAR_COLORS,
        year='compare',
    )

if __name__ == '__main__':
    app.run(debug=True)