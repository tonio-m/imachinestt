FROM python:3.10.4-alpine
# ENV CLICKHOUSE_PORT=9000
# ENV KAFKA_TOPIC_NAME=captcha
# ENV CLICKHOUSE_HOST=localhost
# ENV KAFKA_BOOTSTRAP_SERVER=localhost:9071
WORKDIR /app
ADD . .
RUN sed -i -e 's/v3\.4/edge/g' /etc/apk/repositories \
  && apk upgrade --update-cache --available
RUN apk add build-base librdkafka librdkafka-dev
RUN pip install -r requirements.txt

EXPOSE 8000
WORKDIR /app/src
ENTRYPOINT [ "uvicorn", "main:app" ]
