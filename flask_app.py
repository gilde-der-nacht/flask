#!/usr/bin/env python3

import datetime
import os

import requests
import functools
import collections

from storage import storage
from mail import mailjet
from mail import discord
from flask import Flask, request, json, send_from_directory, Response, redirect

app = Flask(__name__)


def load_config():
    CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = CONFIG_PATH + '/config.json'
    with open(FILE_PATH, 'r') as file:
        config = json.load(file)
        return config


config = load_config()
username = config['auth']['username']
password = config['auth']['password']


mailClient = mailjet.config(
    config['mailjet']['public_key'],
    config['mailjet']['private_key'],
    config['mailjet']['version']
)


def auth_is_valid():
    return request.authorization and (request.authorization.username == username) and (
        request.authorization.password == password)


def auth_required(fun):
    """
    decorator checks/handles if a page/resource should require authentication
    """

    @functools.wraps(fun)
    def decorator(*args, **kwargs):
        if not auth_is_valid():
            return Response('Authentication Required', requests.codes.UNAUTHORIZED,
                            {'WWW-Authenticate': 'Basic realm="Authentication Required"'})
        return fun(*args, **kwargs)

    return decorator


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route('/')
def server_status():
    return 'Olymp is Up &#128154;', requests.codes.OK


@app.route('/resources', methods=['GET'])
def resources_list():
    auth = auth_is_valid()
    all_raw_resources = storage.resources_list()
    all_resources_filtered = []
    for (resource_uid, timestamp, public_body, private_body, url, user_agent) in all_raw_resources:
        resource = {
            'resourceUid': resource_uid,
            'timestamp': timestamp,
            'publicBody': json.loads(public_body),
            'privateBody': json.loads(private_body) if auth else {},
            'url': url if auth else '',
            'userAgent': user_agent if auth else '',
        }
        all_resources_filtered.append(resource)
    return json.dumps(all_resources_filtered), requests.codes.OK


# TODO according to the API description on top, there should be the API version in front of the URL?
# TODO make version with filtering, or add a parameter to enable/disable it??
# TODO add parameter to limit maximum number of rows?
@app.route('/resources/<resource_uid>/entries', methods=['GET'])
def entries_list(resource_uid):
    auth = auth_is_valid()
    all_raw_entries = storage.entries_list(resource_uid)
    all_entries_filtered = []
    for (
            resource_uid, entry_uid, timestamp, identification, public_body, private_body, url,
            user_agent) in all_raw_entries:
        entry = {
            'resourceUid': resource_uid,
            'entryUid': entry_uid,
            'timestamp': timestamp,
            'identification': identification if auth else '',
            'publicBody': json.loads(public_body),
            'privateBody': json.loads(private_body) if auth else {},
            'url': url if auth else '',
            'userAgent': user_agent if auth else '',
        }
        all_entries_filtered.append(entry)
    return json.dumps(all_entries_filtered), requests.codes.OK


@app.route('/resources/<resource_uid>/entries', methods=['POST'])
def entries_add(resource_uid):
    if len(request.data) > 100_000:
        return '', requests.codes.REQUEST_ENTITY_TOO_LARGE
    body = json.loads(request.data)
    identification = body['identification']
    public_body = json.dumps(body['publicBody'])
    private_body = json.dumps(body['privateBody'])
    url = request.url
    user_agent = request.headers.get('User-Agent')
    mail_send(resource_uid, identification, public_body,
              private_body, url, user_agent, 'entries_add')
    entry = storage.entries_add(
        resource_uid, identification, public_body, private_body, url, user_agent)
    entry_uid = entry.get('uid')
    return entry_uid, requests.codes.CREATED


@app.route('/resources/<resource_uid>/entries/<entry_uid>', methods=['GET'])
@auth_required
def get_entry(resource_uid, entry_uid):
    return json.dumps(storage.entries_get(resource_uid, entry_uid))


@app.route('/form/<resource_uid>', methods=['POST'])
def form(resource_uid):
    if len(request.data) > 100_000:
        return '', requests.codes.REQUEST_ENTITY_TOO_LARGE
    PUBLIC_PREFIX = 'public-'
    PRIVATE_PREFIX = 'private-'
    IDENDTIFICATION = 'identification'
    CAPTCHA_SUFFIX = 'captcha'
    LANGUAGE = 'language'
    public = {}
    private = {}
    identification = ''
    spam = False
    language = 'de'
    for key, value in request.form.items():
        if key.endswith(CAPTCHA_SUFFIX):
            spam = (value != '')
        elif key.startswith(PUBLIC_PREFIX):
            public[key[len(PUBLIC_PREFIX):]] = value
        elif key.startswith(PRIVATE_PREFIX):
            private[key[len(PRIVATE_PREFIX):]] = value
        elif key == IDENDTIFICATION:
            identification = value
        elif key == LANGUAGE:
            language = value

    public_body = json.dumps(public)
    private_body = json.dumps(private)
    url = request.headers.get('Referer')
    user_agent = request.headers.get('User-Agent')
    redirect_url = request.form.get('redirect', url)

    if spam:
        return redirect(redirect_url + '?msg=spam')

    entry = storage.entries_add(
        resource_uid, identification, public_body, private_body, url, user_agent)

    config = load_config()

    if ('message' in private) and (len(private['message']) > 0):
        message = private['message']
        msg = f'\'{message}\''
    else:
        msg = 'Nachricht war leer.'

    if 'rollenspieltage.ch' in redirect_url:
        recipient = {
            'email': 'mail@rollenspieltage.ch',
            'name': 'Luzerner Rollenspieltage'
        }
        template = 'rollenspieltage'
    elif 'spieltage.ch' in redirect_url:
        recipient = {
            'email': 'mail@spieltage.ch',
            'name': 'Luzerner Spieltage'
        }
        template = 'spieltage'
    else:
        recipient = {
            'email': 'mail@gildedernacht.ch',
            'name': 'Gilde der Nacht'
        }
        template = 'gilde'

    discord.msg_send(resource_uid, entry, msg, redirect_url,
                     config['discord']['inbox-webhook'])
    mailjet.mail_send(mailClient, msg, {
                      'email': private['email'], 'name': private['name']}, recipient, template, language)

    return redirect(redirect_url + '?msg=success')


# Luzerner Rollenspieltage 2021: Registration
@app.route('/resources/<resource_uid>/register', methods=['POST'])
def register(resource_uid):
    if len(request.data) > 100_000:
        return '', requests.codes.REQUEST_ENTITY_TOO_LARGE
    body = json.loads(request.data)
    secret = body['identification'] if len(
        body['identification']) > 0 else storage.generate_uid()
    public_body = json.dumps(body['publicBody'])
    private_body = json.dumps(body['privateBody'])
    url = request.url
    user_agent = request.headers.get('User-Agent')
    entry = storage.entries_add(
        resource_uid, secret, public_body, private_body, url, user_agent)

    public = json.loads(public_body)
    language = public.get('interfaceLanguage') or 'de'

    private = json.loads(private_body)
    name = private.get('intro').get('name')
    email = private.get('intro').get('email')
    questions = private.get('outro').get('questions')

    langPrefix = ('/' + language) if language == 'en' else ''
    edit_link = 'https://rollenspieltage.ch' + \
        langPrefix + '/edit?secret=' + secret

    discord.msg_send(resource_uid, entry, questions, 'Anmeldung Rollenspieltage 2021 (' + language + ')',
                     config['discord']['inbox-webhook'])
    mailjet.mail_send(mailClient, edit_link, {
                      'email': email, 'name': name}, {
        'email': 'mail@rollenspieltage.ch',
        'name': 'Luzerner Rollenspieltage'
    }, 'rollenspieltage', language, 'rollenspieltage2021')

    return json.dumps({'entry_uid': entry.get('uid'), 'secret': secret}), requests.codes.CREATED


@app.route('/resources/<resource_uid>/registration/<secret>', methods=['GET'])
def get_registration(resource_uid, secret):
    entry_list = storage.entries_list(resource_uid)
    registration_entry = None
    for (resource_uid, entry_uid, timestamp, identification, public_body, private_body, _url, _user_agent) in entry_list:
        if (identification == secret):
            registration_entry = {
                'resourceUid': resource_uid,
                'entryUid': entry_uid,
                'timestamp': timestamp,
                'secret': identification,
                'publicBody': json.loads(public_body),
                'privateBody': json.loads(private_body),
            }

    if (registration_entry is None):
        return '', requests.codes.UNAUTHORIZED
    return json.dumps(registration_entry)


@app.route('/admin')
@auth_required
def admin():
    return send_from_directory('static', 'admin.html')


@app.route('/olymp.js')
def js():
    return send_from_directory('static', 'olymp.js')


@app.route('/status')
def status():
    status = {
        'version': '1.0.1',
        'time': datetime.datetime.now().isoformat(),
    }
    return json.dumps(status), requests.codes.OK
