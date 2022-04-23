from pydantic import BaseModel


class CaptchaEvent(BaseModel):
    time: str
    type: str
    site_id: str
    correlation_id: str
