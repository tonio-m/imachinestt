import sys
import json
import pytest
import requests
from uuid import UUID
from os import environ
from pydantic import BaseModel
sys.path.append("../src/")
from models import CaptchaEvent


CLICKHOUSE_HOST=environ['CLICKHOUSE_HOST']
KAFKA_TOPIC_NAME=environ['KAFKA_TOPIC_NAME']
CLICKHOUSE_PORT=int(environ['CLICKHOUSE_PORT'])
KAFKA_BOOTSTRAP_SERVER=environ['KAFKA_BOOTSTRAP_SERVER']


class Counter(BaseModel):
    date: str
    site_id: UUID
    served : int
    solved : int


class PostEventResponse(BaseModel):
    topic = KAFKA_TOPIC_NAME
    message: str
    status: str


def test_post_event():
    event = {
        "site_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "type": "serve",
        "correlation_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "time": "2001-01-01T05:55:07"
    }
    CaptchaEvent(**event)
    data = json.dumps(event)
    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://localhost:8000/v1/event', headers=headers, data=data)
    assert response.status_code == 200
    body = response.json()
    PostEventResponse(**body)


def test_get_report():
    headers = { 'Content-Type': 'application/json' }
    response = requests.get('http://localhost:8000/v1/report', headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert 'counters' in body
    if len(body['counters']) > 0:
        counter = body['counters'][0]
        Counter(**counter)

# def test_flow():
#     headers = { 'Content-Type': 'application/json' }
#     params = (('site_id', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'))
#     response = requests.get('http://localhost:8000/v1/report', headers=headers, params=params)
#     assert response.status_code == 200
#     assert 'counters' in response
#     if len(response['counters']) > 0:
#         counter = response['counters'][0]
#         Counter(**counter)

