import sys
import json
import random
from faker import Faker
 

faker = Faker()
Faker.seed(42)
 

def generate_data(n):
    corr_ids = [ faker.uuid4() for i in range(n//10)]
    site_ids = [ faker.uuid4() for i in range(n//10)]
    corr_ids += [random.choice(corr_ids) for i in range(n//100)]
    site_ids += [random.choice(site_ids) for i in range(n//100)]

    return [
        {
            'site_id': random.choice(site_ids),
            'type': random.choice(['serve','solve']),
            'correlation_id': random.choice(corr_ids),
            'time': faker.date_time_between(start_date='-1y', end_date='now').isoformat()
        }
    for i in range(n)]

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename,'w') as f:
        data = generate_data(10000)
        for doc in data:
            f.write(json.dumps(doc))
            f.write('\n')
