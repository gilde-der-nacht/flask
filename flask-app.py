#!/usr/bin/env python3

# export FLASK_APP=flask-app.py
# export FLASK_ENV=development
# flask run

# This flask microservice accepts REST requests as follows:
#
# storage:
#   there are two kinds of data
#       resources   -> buckets for entries of the same kind, enriched with a email address
#       entries     -> saved data (eg. form data or registrations for events),
#           two main data sets (JSON format):
#               public  -> public data, everybody can read
#               private -> only access with authentication
#
# domain: api.gildedernacht.ch/v1/
#   '/resources'                     -> interact with ALL the resources
#   '/resources/{uid}'               -> interact with ONE resource
#   '/resources/{uid}/entries'       -> interact with ALL entries of one resource
#   '/resources/{uid}/entries/{uid}' -> interact with ONE entry
#
# methods:
#   GET     -> read all data (if not authenticated, only public data)
#   POST    -> write new data
#   PUT     -> write a copied entry which does update some data (doesn't override anything)
#   DELETE  -> write a copied entry with the status 'deleted' (doesn't override anything)

import datetime

import requests
from flask import Flask, request, abort, json, send_from_directory
from storage import storage

app = Flask(__name__)


@app.route('/')
def server_status():
    return '&#128154; Flask is running', requests.codes.OK


# GET: get all resources    -> UID, public (description), private (email address)
# POST: add new resource    -> public (description), private (email address), only if authenticated
# PUT: not allowed
# DELETE: not allowed
# TODO comment partially repeats the code, is obvious from the following line, which methods are supported
@app.route('/resources', methods=['GET', 'POST'])
def resources():
    if request.method != 'GET' and request.method != 'POST':
        abort(requests.codes.METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        return 'check'
        # all_resources = storage.read_all('resources')

    # TODO use an elif, if it was a GET it is impossible to be a POST
    if request.method == 'POST':
        # public_body = request.data.get('public_body')
        # private_body = request.data.get('private_body')
        data = request.data
        # return str(json.loads(request.get_json()))
        # storage.write(public_body, private_body)
        return 'b3e35dfa2cd27cd385f08c246b6d49cf2e991c894d96828ba355063e77723fc0', requests.codes.CREATED


# @app.route('/post-json-to-container/uid/<uid>', methods=['POST'])
# def post_json_to_container(uid):
#     # naming, we do not return a container we actually return the entries, /container/.../<uid> may return some statistics about the container or nothing at all
#
#     if request.method != 'POST':
#         abort(status_codes.StatusCode.HTTP_405_METHOD_NOT_ALLOWED)
#
#     try:
#         # you used a 'form' here, but this measn we have to generate a form with JS and inside the test, maybe this is the better idea, but client/server need to be both updated then, we can avoid the dumps so it may be worth to investigate
#         received_data = request.get_data()
#         received_json = json.loads(received_data)
#
#         public_body = json.dumps(received_json['public'])
#         private_body = json.dumps(received_json['private'])
#
#         storage.write(uid, public_body, private_body)
#
#     except ValueError:
#         abort(status_codes.StatusCode.HTTP_400_BAD_REQUEST)
#
#     return '{}'


# @app.route('/get-json-from-container/uid/<uid>')
# def get_json_from_container(uid):
#     # TODO exception handling?
#     # TODO use ''.format or f''
#
#     try:
#         container = storage.read(uid)
#     except ValueError:
#         abort(status_codes.StatusCode.HTTP_400_BAD_REQUEST)
#
#     container_list = []
#
#     if False:
#         for row in container:
#             # I removed the logic to merge container, ... what if we later add another method to return all entries? maybe we like to use the same code to display then, but in this case we have to differentiate between two possible results
#             container_list.append(
#                 '''
#                     {
#                         'container_uid': '%s',
#                         'entry_uid': '%s',
#                         'public': '%s',
#                         'private': '%s',
#                         'timestamp': '%s'
#                     }
#                 ''' % (row[0], row[1], row[2], row[3], row[4])
#
#             )
#             print(row)
#
#         json_output = '[' + ', '.join(container_list) + ']';
#
#     # simpler?
#
#     if False:
#         def convert(entry):
#             return '{{'container_uid': '{0}', 'entry_uid': '{1}', 'public': '{2}', 'private': '{3}', 'timestamp': '{4}'}}'.format(
#                 *entry)
#
#         container_list = map(convert, container)
#         json_output = '[' + ', '.join(container_list) + ']';
#
#     # better? we do not assemble json ourself ...
#
#     if True:
#         def convert(entry):
#             return {'container_uid': entry[0], 'entry_uid': entry[1], 'public': json.loads(entry[2]),
#                     'private': json.loads(entry[3]), 'timestamp': entry[4]}
#
#         container_list = map(convert, container)
#         json_output = json.dumps(list(container_list))
#
#     return json_output


# TODO authentication
@app.route('/admin')
def admin():
    return send_from_directory('static', 'admin.html')


# TODO authentication
@app.route('/test')
def test():
    return send_from_directory('static', 'test.html')


# TODO use the name of the application here
@app.route('/app.js')
def js():
    return send_from_directory('static', 'app.js')


# TODO add api version so clients can test for an API and there may also be backward compatbility for the future
@app.route('/status')
def status():
    return json.dumps({
        'version': '0.0.0',
        'time': datetime.datetime.now().isoformat(),
    })
