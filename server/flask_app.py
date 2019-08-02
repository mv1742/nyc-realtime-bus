from flask import Flask, Response

import os
import numpy as np
import json
from functools import singledispatch

from get_bus_locations import get_bus_locations, get_route_info

@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@to_serializable.register(np.int64)
def ts_int64(val):
    """Used if *val* is an instance of numpy.float32."""
    return val.item()

key = os.getenv("MTA_KEY")

app = Flask(__name__, static_url_path='', static_folder='.')
# app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/realtime/<line>')
def realtime(line):
    response = json.dumps(get_bus_locations(key, line))

    return Response(response,
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/busdata/<line>')
def busdata(line):
    response = json.dumps(get_route_info(line), default=to_serializable)

    return Response(response,
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)