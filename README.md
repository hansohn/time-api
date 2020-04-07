# time-api

[![GitHub tag](https://img.shields.io/github/tag/hansohn/time-api.svg)](https://github.com/hansohn/time-api)

[Flask](https://flask.palletsprojects.com/en/1.1.x/) API that returns the current datetime in [ISO8601](https://www.iso.org/iso-8601-date-and-time-format.html) format.

### Running with Flask

This application was built and tested with Python `3.7`. To begin, install prerequisites and launch application.

```bash
# install prerequisites
pip install -r requirements.txt

# launch application
cd ./app/
flask run
```

Once the application is running you can query [http://127.0.0.1:5000/api/v1/](http://127.0.0.1:5000/api/v1/) for the current datetime response.

```json
{
  "datetime": "2020-04-06T23:05:11.004794",
  "version": 1
}
```

### Running with Docker

Build [Docker](https://www.docker.com/) image and run it. Requires Docker to already be installed and running.

```bash
docker build --tag time:1.0 .
docker run --publish 5000:5000 --detach --name time time:1.0
```

### Load Testing with Docker Compose

There are two load tests  packaged within this repo. The more popular **[Locust](https://locust.io/)** load test and my homegrown solution, **Simple Load Test**. I have included [Docker Compose](https://docs.docker.com/compose/) files for both types to ease with setup and communication.

#### Locust

Build and launch docker containers. Requires Docker and Docker Compose to already be installed and running.


```bash
# build and launch docker containers
docker-compose -f docker-compose-locust.yml build
docker-compuse -f docker-compose-locust.yml up
```

Navigate to http://127.0.0.1:8089 in your browser and fill in the desired values for **Number of total users to simulate** and **Hatch rate (users spawned/second)**. Select **Start Swimming** when ready to begin test.

#### Simple Load Test

Build and launch docker containers.

```bash
# build and launch docker containers
docker-compose -f docker-compose-simple.yml build
docker-compuse -f docker-compose-simple.yml up
```

Once launched, load testing will commence immediately, and you will see a similar response to the following output:

```bash
Recreating time-api_time_1 ... done
Recreating time-api_simple_1 ... done
Attaching to time-api_time_1, time-api_simple_1
time_1    |  * Serving Flask app "app.py"
time_1    |  * Environment: production
time_1    |    WARNING: This is a development server. Do not use it in a production deployment.
time_1    |    Use a production WSGI server instead.
time_1    |  * Debug mode: off
simple_1  | [-- SIMPLE LOAD TEST --]
simple_1  |
simple_1  | [params]
simple_1  | target url: 'http://time:5000'
simple_1  | request count: 1000
simple_1  | requests per sec: 100
simple_1  | max threads: 100
simple_1  |
simple_1  | test in progress ...
simple_1  | test complete! please wait while we gather metrics ...
simple_1  |
simple_1  | [results]
simple_1  | total requests sent: 1000
simple_1  | requests per sec: 87.1
simple_1  | passed: 1000, failed: 0
simple_1  | ttlb mean avg: 0.004 seconds
simple_1  | ttlb median avg: 0.004 seconds
simple_1  |
simple_1  | Load test completed in 11.482 seconds
time-api_simple_1 exited with code 0
```
