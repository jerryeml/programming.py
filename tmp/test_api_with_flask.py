import logging
import json
import requests
import pytest
from threading import Thread
from tmp import api_with_flask


@pytest.fixture(scope="module", autouse=True)
def setup():
    # Start running mock server in a separate thread.
    # Daemon threads automatically shut down when the main process exits.
    mock_server_thread = Thread(target=api_with_flask.init_api)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()


def test_avengers_all_with_get_method():
    rtn = requests.get(url='http://localhost:5000/get/avengers/all')
    print(f'status code: {rtn.status_code}')
    assert rtn.status_code == 200
    print(f'response: {json.loads(rtn.content)}')
    
    expect_content = [
        {
            "Leader": "Tony", 
            "gender": "M", 
            "id": 1, 
            "nationality": "American", 
            "nickname": "iron man", 
            "superpower": "n"
        }, 
        {
            "Leader": "Peter", 
            "gender": "M", 
            "id": 2, 
            "nationality": "American", 
            "nickname": "spider man", 
            "superpower": "y"
        }, 
        {
            "Leader": "Natasha", 
            "gender": "F", 
            "id": 3, 
            "nationality": "Russia", 
            "nickname": "Block Widow", 
            "superpower": "n"
        }
    ]
    assert json.loads(rtn.content) == expect_content


def test_avengers_all_with_post_method():
    rtn = requests.post(url='http://localhost:5000/get/avengers/all')
    print(f'status code: {rtn.status_code}')
    assert rtn.status_code == 405