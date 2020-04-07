# -*- coding: utf-8 -*-

from datetime import datetime
from flask import Flask, jsonify
from flask_restful import Resource, Api
import logging

"""
time-api
"""

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
api = Api(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

class HelloWorld(Resource):
    def get(self):
        return {'msg': 'Hello World!'}


class TimeV1(Resource):
    def get(self):
        m = {'datetime':format(datetime.isoformat(datetime.now())),
             'version':1}
        return jsonify(m)


api.add_resource(HelloWorld, '/')
api.add_resource(TimeV1, '/api/v1/')

if __name__ == "__main__":
    app.run()
