'use strict';

/*
This script is full of somewhat more modern JavaScript:

async/await, fetch, class, ...

If there is problem that not all devices support this newer this JavaScript
keywords, this script itself can be "compiled" to an older JavaScript standard with

Babel

https://babeljs.io/

sudo npm install @babel/core @babel/cli @babel/preset-env

babel olymp.js
*/

/*
A thin wrapper around the Fetch API

https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
*/
class HTTP {
    /*
    Ideally this HTTP codes would be a "static const" part of the HTTP class,
    but this seems to be impossible with the current (2019) JavaScript standards. If anyone
    who reads this has a more JS-alike idea how to express the same idea, please let us know.

    Usage:

    HTTP.CODES.OK_200
    */
    static get CODES() {
        return {
            CONTINUE_100: 100,
            SWITCHING_PROTOCOLS_101: 101,
            OK_200: 200,
            CREATED_201: 201,
            ACCEPTED_202: 202,
            NON_AUTHORITATIVE_INFORMATION_203: 203,
            NO_CONTENT_204: 204,
            RESET_CONTENT_205: 205,
            PARTIAL_CONTENT_206: 206,
            MULTIPLE_CHOICES_300: 300,
            MOVED_PERMANENTLY_301: 301,
            FOUND_302: 302,
            SEE_OTHER_303: 303,
            NOT_MODIFIED_304: 304,
            USE_PROXY_305: 305,
            RESERVED_306: 306,
            TEMPORARY_REDIRECT_307: 307,
            BAD_REQUEST_400: 400,
            UNAUTHORIZED_401: 401,
            PAYMENT_REQUIRED_402: 402,
            FORBIDDEN_403: 403,
            NOT_FOUND_404: 404,
            METHOD_NOT_ALLOWED_405: 405,
            NOT_ACCEPTABLE_406: 406,
            PROXY_AUTHENTICATION_REQUIRED_407: 407,
            REQUEST_TIMEOUT_408: 408,
            CONFLICT_409: 409,
            GONE_410: 410,
            LENGTH_REQUIRED_411: 411,
            PRECONDITION_FAILED_412: 412,
            REQUEST_ENTITY_TOO_LARGE_413: 413,
            REQUEST_URI_TOO_LONG_414: 414,
            UNSUPPORTED_MEDIA_TYPE_415: 415,
            REQUESTED_RANGE_NOT_SATISFIABLE_416: 416,
            EXPECTATION_FAILED_417: 417,
            PRECONDITION_REQUIRED_428: 428,
            TOO_MANY_REQUESTS_429: 429,
            REQUEST_HEADER_FIELDS_TOO_LARGE_431: 431,
            INTERNAL_SERVER_ERROR_500: 500,
            NOT_IMPLEMENTED_501: 501,
            BAD_GATEWAY_502: 502,
            SERVICE_UNAVAILABLE_503: 503,
            GATEWAY_TIMEOUT_504: 504,
            HTTP_VERSION_NOT_SUPPORTED_505: 505,
            NETWORK_AUTHENTICATION_REQUIRED_511: 511,
        };
    }

    static async get(path) {
        const response = await fetch(path);
        const text = await response.text();
        return [text, response.status]
    }

    static async post(path, data) {
        const response = await fetch(path, {
            method: 'POST',
            body: data,
        });
        const text = await response.text();
        return [text, response.status]
    }

    static async put(path, data) {
        const response = await fetch(path, {
            method: 'PUT',
            body: data,
        });
        const text = await response.text();
        return [text, response.status]
    }

    static async delete(path) {
        const response = await fetch(path, {
            method: 'DELETE',
        });
        const text = await response.text();
        return [text, response.status]
    }
}

const SERVER = document.location.origin.includes('127.0.0.1') ? document.location.origin :'https://api.gildedernacht.ch';

/*
This is the main class which allows an easy access to the Olymp server.

At the moment the SERVER is hardcoded, it may be an idea to make the functions
not static anymore and provide a constructor with the option to set the server
explicitly.
*/
class Olymp {
    /*
    The _verify functions are not here to protect against malicious intent (which is impossible),
    but to give the user of this class an early feedback if a parameter is invalid.

    At the moment _verifyUid & _verifyBody do not directly call _verify, because both functions
    are tested externally. Something which may reveal too much details.
    */

    static _verify(condition) {
        if(!condition) {
            throw 'Invalid Parameter';
        }
    }

    static _verifyUid(uid) {
        return (uid.length === 64) && RegExp('[0-9a-f]{64}').test(uid)
    }

    static _verifyBody(body) {
        return (typeof body) === 'object';
    }

    static async status() {
        const path = `${SERVER}/status`;
        const [text, status] = await HTTP.get(path);
        if(status !== HTTP.CODES.OK_200) {
            throw 'Invalid Response';
        }
        return JSON.parse(text);
    }

    static async entriesAdd(resourceUid, publicBody, privateBody) {
        Olymp._verify(Olymp._verifyUid(resourceUid));
        Olymp._verify(Olymp._verifyBody(publicBody));
        Olymp._verify(Olymp._verifyBody(privateBody));
        const path = `${SERVER}/resources/${resourceUid}/entries`;
        const data = {
            'publicBody': publicBody,
            'privateBody': privateBody,
        };
        const [_, status] = await HTTP.post(path, JSON.stringify(data));
        if(status !== HTTP.CODES.CREATED_201) {
            throw 'Invalid Response';
        }
    }

    static async entriesList(resourceUid) {
        Olymp._verify(Olymp._verifyUid(resourceUid));
        const path = `${SERVER}/resources/${resourceUid}/entries`;
        const [text, status] = await HTTP.get(path);
        if(status !== HTTP.CODES.OK_200) {
            throw 'Invalid Response';
        }
        return JSON.parse(text);
    }

    // TODO add a function which acts like entriesList, but only return the most recent entry in case two entries have the same public and/or private body
}
