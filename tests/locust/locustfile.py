#!/usr/bin/env python
# -*- coding: utf-8 -*-

from locust import HttpLocust, TaskSet, task, between

"""
locust load test
"""


class BasicTaskSet(TaskSet):
    @task
    def index(self):
        self.client.get("/api/v1/")


class BasicTasks(HttpLocust):
    task_set = BasicTaskSet
    wait_time = between(5.0, 9.0)
