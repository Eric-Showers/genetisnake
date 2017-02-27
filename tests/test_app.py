import json
import pytest
import genetisnake.app

@pytest.fixture
def app():
    return genetisnake.app.application

def do_test_start(client, root):
    data = {"width":20,"height":20,"game_id":"example-game-id"}
    res = client.post(root + '/start',
                      data=json.dumps(data),
                      content_type='application/json')
    assert res.status_code == 200
    data = res.json
    assert set(data.keys()) <= set(("color", "head_url", "name", "taunt"))
    assert data["head_url"].startswith('http')

    res = client.get(data["head_url"])
    assert res.status_code == 200

def do_test_move(client, root):
    data = {
        "you": "5b079dcd-0494-4afd-a08e-72c9a7c2d983",
        "width": 2,
        "turn": 0,
        "snakes": [
            {
                "taunt": "git gud",
                "name": "my-snake",
                "id": "5b079dcd-0494-4afd-a08e-72c9a7c2d983",
                "health_points": 93,
                "coords": [[0,0], [0,0], [0,0]]
            },
            {
                "taunt": "gotta go fast",
                "name": "other-snake",
                "id": "9116ef2a-51c1-4fb5-9b3f-b5d3fbfcbef6",
                "health_points": 50,
                "coords": [[1,0], [1,0], [1,0]]
            }
        ],
        "height": 2,
        "game_id": "aecf53b9-c7f2-4f5d-bc3f-cd14cb8338f0",
        "food": [ [1,1] ],
        "board": [
            [
                {
                    "state": "head",
                    "snake": "my-snake"
                },
                {
                    "state": "empty"
                }
            ],
            [
                {
                    "state": "head",
                    "snake": "other-snake"
                },
                {
                    "state": "food"
                }
            ]
        ]
    }
    res = client.post(root + '/move',
                      data=json.dumps(data),
                      content_type='application/json')
    assert res.status_code == 200
    assert res.json["move"] in "up down left right".split()

def test_start(client):
    do_test_start(client, "")
    
def test_move(client):
    do_test_move(client, "")

def test_greedy_start(client):
    do_test_start(client, "greedy")
    
def test_greedy_move(client):
    do_test_move(client, "greedy")

def test_trainee_start(client):
    do_test_start(client, "trainee")
    
def test_trainee_move(client):
    do_test_move(client, "trainee")

def test_index(client):
    res = client.get('/', follow_redirects=True)
    assert res.status_code == 200
    
