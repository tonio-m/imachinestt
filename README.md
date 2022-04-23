# Kafka/Clickhouse/Python Challenge

Homework for Kafka/Clickhouse/Python candidates

## Overview

The task is to build the webserver which accepts incoming captcha events in json format, puts them to clickhouse using kafka and then serves aggregated statistics. 

## Requirements

### Option 1

The application must have a RESTful api with 2 endpoints, one for ingesting, one for serving aggregated statistics. There has to be a kafka topic in between, and clickhouse as a storage/aggregation layer.

### Option 2

Focus more on CI/CD pipeline, infrastructure deployment and configuration, and operating the tool.

If you'd like to tweak the design, please ask your interviewer if you have a better way of approaching the problem.

## Incoming event structure
Incoming event has the following structure
- **time**: time of the event (string UTC isoformat)
- **type**: type of the event may be one of `serve` or `solve` (string)
- **correlation_id**: id of the whole captcha procedure (maybe be same across different types, new procedure should get a new ID) (uuid)
- **site_id**: id of site captcha is installed on (uuid) - grouping key

### Example
``` bash
curl http://localhost:8000/api/event -X POST -d '{"time": "2021-01-22T18:20:42.159246", "type": "serve", "correlation_id": "357d1bc4-3502-4592-8355-874b1c31f1a6", "site_id": "0faf8b64-a33d-4db8-aaee-aa165d13cff6"}' -H 'Content-Type: application/json'
```

## Output statistics
You have to aggregate the number of captcha served and solved in two separate counters grouped by site_id and day (00:00:00 time) and present them with another REST API, plus a filter on `site_id` in query params would be plausible.

- **served**: number of served captcha (int)
- **solved**: number of solved captcha (int)

``` bash
curl http://localhost:8000/api/report -H 'Accept: application/json'
```

``` js
{
    "counters: [{
        "time": "2021-01-25T00:00:00",
        "site_id": "357d1bc4-3502-4592-8355-874b1c31f1a6",
        "served": 10,
        "solved": 10
    }]
}
```

## Events de-duplication
Events can possibly come into the system duplicated with the same `type` and `correlation_id`, you have to de-duplicate the events and not include the duplicates inside
the counters.

## Scalability
Please keep in mind the server might get a lot of requests and has to scale horizontally, if there is not enough time for implementation,
at least a summary of the approach to horizontal scaling would be fine.

## Testing
You may use your favourite python frameworks, but please test the two endpoints with a couple of integration tests


# Submission
Create a PR to this repo when ready with your result, which we'll use to ask questions and review with you.

## Timeline
**You shouldn't spend more than 8 hours on this, so by design it will be intentionally sparse.** This helps us understand your ability to prioritize what is important.

**Please provide your solution within 72 hours of reading this.**


## Expectations
Treat this as you would a real-world **prototype** project that would be used and modified by others in the future, i.e., documentation, tests, etc.  

You aren't expected to make a full production ready system, but you are expected to consider what a production ready system would look like and craft the solution to be able to add the features that you don't have time for, at another time.

Ask as many questions as you want to ensure that we're on the same page in terms of what is required.

#### Focus On
- Code Legibility
- Clear Documentation
- Test Coverage - Mostly integration
- Fully Functional

If you have any questions please let us know!  Good luck!

# Bonus Points
Below outlines additional options that correlate with our daily operation and can better demonstrate your capability / skill in these different areas. The options are assigned varying difficulties that can net you a better score.

### Schema validation *(easy)*
Use any library for easy schema validation of requests, models, and responses

### Query filters *(easy)*
Enable the statistics endpoint to filter out a given sitekey or day and present only relevant counters

### Async support *(hard)*
Implement the webserver with python async

### Api versioning *(medium)*
Enable the framework to increase api's versions easily, for example change `/v1/event` to `/v2/event` and use a completely different schema.

### Clickhouse migrations *(medium)*
Enable clickhouse schema migrations mechanism
