import json


def index():
    return json.dumps({'1214': 'regerg'})


def return_405():
    return json.dumps({'Error': 'Method not allowed'})


def return_404():
    return json.dumps({'Error': 'Not found'})