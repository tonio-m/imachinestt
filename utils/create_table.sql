CREATE TABLE captcha
(
    site_id UUID,
    time DateTime,
    correlation_id UUID,
    event_type String
) ENGINE = MergeTree ORDER BY (time,site_id,correlation_id,event_type)


CREATE TABLE default.captcha_queue
(
    site_id UUID,
    time DateTime,
    correlation_id UUID,
    event_type String
)
   ENGINE = Kafka('kafka.confluent.svc.cluster.local:9071', 'captcha', 'clickhouse',
            'JSONEachRow') settings kafka_thread_per_consumer = 0, kafka_num_consumers = 1;


CREATE MATERIALIZED VIEW default.captcha_mv TO default.captcha AS
SELECT *
FROM default.captcha_queue;
