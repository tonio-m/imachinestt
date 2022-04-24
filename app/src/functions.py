from clickhouse_driver import Client
from confluent_kafka import Producer


async def send_kafka_message(bootstrap_server: str, topic: str, message: str) -> dict:
    try:
        p = Producer({'bootstrap.servers': bootstrap_server})
        p.produce(topic, message)
        p.flush()
        status = "message sent successfully"
    except Exception:
        status = "error sending message"
    return { "topic": topic, "message": message, "status": status}


async def query_report(host: str, port: int, site_ids: list[str]) -> dict:
    client = Client(host=host,port=port)

    where_statement = ""
    replacement_variables = {}
    if len(site_ids) > 0:
        conditions = [f'site_id = %(site_id{i})s' for i in range(len(site_ids))]
        replacement_variables = {f'site_id{i}': site_id for i,site_id in enumerate(site_ids)}
        where_statement = 'WHERE ' + ' OR '.join(conditions)

    query = f"""
    SELECT
        toDate(time) AS date,
        site_id AS site_id,
        type,
        count(type) AS count
    FROM captcha
    {where_statement} 
    GROUP BY date, site_id, type;
    """
    results = client.execute(query,replacement_variables)
    results_dic = await __results_to_dict(results)
    return results_dic


async def __results_to_dict(results: list[list]) -> dict:
    if len(results) > 0:
        results = [
            [
                row[0].isoformat(),
                row[1],
                row[2],
                row[3]
            ] for row in results]
        result_dic = {}
        [result_dic.setdefault(row[0],dict()) for row in results]
        [result_dic[row[0]].setdefault(row[1],dict()) for row in results]
        [result_dic[row[0]][row[1]].setdefault(row[2],row[3]) for row in results]
    else:
        result_dic = {}
    return result_dic
