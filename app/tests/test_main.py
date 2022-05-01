import sys
import json
import pytest
import requests
from uuid import UUID
from os import environ
from pydantic import BaseModel
sys.path.append("src/")
from models import CaptchaEvent


API_URL=environ['API_URL'].strip('/')


class Counter(BaseModel):
    date: str
    site_id: UUID
    served : int
    solved : int


class PostEventResponse(BaseModel):
    topic: str
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
    response = requests.post(f'{API_URL}/event', headers=headers, data=data)
    assert response.status_code == 200
    body = response.json()
    PostEventResponse(**body)


def test_get_report():
    headers = { 'Content-Type': 'application/json' }
    response = requests.get(f'{API_URL}/report', headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert 'counters' in body
    if len(body['counters']) > 0:
        counter = body['counters'][0]
        Counter(**counter)
