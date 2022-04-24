import json
from os import environ
from typing import Optional
from models import CaptchaEvent
from fastapi import FastAPI, Query
from fastapi_versioning import VersionedFastAPI, version
from functions import query_report, send_kafka_message


CLICKHOUSE_HOST=environ['CLICKHOUSE_HOST']
KAFKA_TOPIC_NAME=environ['KAFKA_TOPIC_NAME']
CLICKHOUSE_PORT=int(environ['CLICKHOUSE_PORT'])
KAFKA_BOOTSTRAP_SERVER=environ['KAFKA_BOOTSTRAP_SERVER']


app = FastAPI()


@app.get("/")
async def root() -> str:
    return "ok"


@app.post("/event")
@version(1)
async def post_event(event: CaptchaEvent) -> dict:
    message = json.dumps(event.dict())
    result = await send_kafka_message(KAFKA_BOOTSTRAP_SERVER,KAFKA_TOPIC_NAME,message)
    return result


@app.get("/report")
@version(1)
async def get_report(site_id: Optional[list[str]] = Query(None)) -> dict:
    if site_id is None:
        site_id = []
    results_dic = await query_report(CLICKHOUSE_HOST, CLICKHOUSE_PORT, site_id)
    return results_dic


app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}',
    enable_latest=True)
