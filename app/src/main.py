import json
from typing import Optional
from models import CaptchaEvent
from fastapi import FastAPI, Query
from fastapi_versioning import VersionedFastAPI, version
from functions import query_metrics, send_kafka_message


CLICKHOUSE_PORT=9000
KAFKA_TOPIC_NAME='captcha'
CLICKHOUSE_HOST='localhost'
KAFKA_BOOTSTRAP_SERVER='localhost:9071'


app = FastAPI()


@app.get("/")
async def root() -> str:
    return "ok"


@app.post("/events")
@version(1)
async def post_events(event: CaptchaEvent) -> dict:
    message = json.dumps(event.dict())
    result = await send_kafka_message(KAFKA_BOOTSTRAP_SERVER,KAFKA_TOPIC_NAME,message)
    return result


@app.get("/metrics")
@version(1)
async def get_metrics(site_id: Optional[list[str]] = Query(None)) -> dict:
    if site_id is None:
        site_id = []
    results_dic = await query_metrics(CLICKHOUSE_HOST, CLICKHOUSE_PORT, site_id)
    return results_dic


app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}',
    enable_latest=True)
