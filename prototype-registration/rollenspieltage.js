'use strict';


/*
TODO
how portable is this? better use a library?
https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest
https://www.npmjs.com/package/js-sha256
add this to the library
await is somehow not expected here IMHO as it is just a calculation
some kind of hmac would be better? or else an attacker can try out email addresses
ask the server to apply some kind of encrpytion on specific fields?
maybe there is no public/private generated by the client, but by the server and the client requests to 'hide/encrypt' elements
*/
async function digest(message) {

    async function digestMessage(message) {
        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        const result = await window.crypto.subtle.digest('SHA-256', data);
        return result;
    }

    function hexString(buffer) {
        const byteArray = new Uint8Array(buffer);
        const hexCodes = [...byteArray].map(value => {
            const hexCode = value.toString(16);
            const paddedHexCode = hexCode.padStart(2, '0');
            return paddedHexCode;
        });
        return hexCodes.join('');
    }

    return hexString(await digestMessage(message));
}

function replaceWithFragment(node, fragment) {
    node.innerHTML = ''; // ugly?
    node.appendChild(fragment);
}

function getGames() {
    return {
        'Adrian-0': {
            name: 'Shadowrun',
            gm: 'Adrian',
            gameDescription: 'Dystopisch BlaBla ...',
            campaignDescription: 'BlaBla ...',
            lang: 'DE',
            playersMax: 5,
        },
        'Manuela-0': {
            name: 'Finsterwald',
            gm: 'Manuela',
            gameDescription: 'Steampunk Blabla ...',
            campaignDescription: 'BlaBla ...',
            lang: 'DE',
            playersMax: 4,
        },
        'EnglishMan-0': {
            name: 'D&D',
            gm: 'EnglishMan',
            gameDescription: 'D & D Blabla ...',
            campaignDescription: 'Hack & Slash BlaBla ...',
            lang: 'EN',
            playersMax: 2,
        },
    };
}

function getRounds() {
    return {
        'Adrian-0': { gameId: 'Adrian-0', day: 'friday', from: 13, to: 15 },
        'Adrian-1': { gameId: 'Adrian-0', day: 'friday', from: 15, to: 17 },
        'Adrian-2': { gameId: 'Adrian-0', day: 'saturday', from: 13, to: 15 },

        'Manuela-0': { gameId: 'Manuela-0', day: 'friday', from: 13, to: 15 },
        'Manuela-1': { gameId: 'Manuela-0', day: 'friday', from: 15, to: 17 },
        'Manuela-2': { gameId: 'Manuela-0', day: 'saturday', from: 13, to: 15 },

        'EnglishMan-0': { gameId: 'EnglishMan-0', day: 'friday', from: 13, to: 15 },
        'EnglishMan-1': { gameId: 'EnglishMan-0', day: 'friday', from: 15, to: 17 },
        'EnglishMan-2': { gameId: 'EnglishMan-0', day: 'saturday', from: 13, to: 15 },
    };
}

async function getRegistrations() {
    /*
    TODO check api and log error if it doesn't match
    const status = await App.status();
    console.log(status);
    console.assert(status.version === '0.0.0');
    */

    const REGISTRATION_UID = '...';
    //const registrations = await App.getEntries(REGISTRATION_UID);
    const registrationsAll = [
        {publicBody: {roundId: 'Adrian-0', userId: '1'}, privateBody: {name: 'a', email: 'a@unknown.tld'}},
        {publicBody: {roundId: 'Adrian-0', userId: '2'}, privateBody: {name: 'b', email: 'b@unknown.tld'}},
        {publicBody: {roundId: 'Adrian-0', userId: '3'}, privateBody: {name: 'c', email: 'c@unknown.tld'}},
        {publicBody: {roundId: 'Adrian-0', userId: '4'}, privateBody: {name: 'd', email: 'd@unknown.tld'}},
        {publicBody: {roundId: 'Adrian-0', userId: '5'}, privateBody: {name: 'e', email: 'e@unknown.tld'}},

        {publicBody: {roundId: 'Adrian-1', userId: '1'}, privateBody: {name: 'a', email: 'a@unknown.tld'}},
    ];

    // TODO filter double/triple/... regstriations, only take the most recent one, add this function to the library as everyone using the API quite likely has the same requirement
    const registrations = registrationsAll;

    return registrations;
}


async function submitRegistration(name, email, comment) {
    // TODO game selection missing

    const userId = await digest(email);

    const publicBody = {
        roundId: '',
        userId: userId,
    };
    const privateBody = {
        name: name,
        email: email,
        comment: comment,
    };

    console.log('submitRegistration ' + JSON.stringify(publicBody) + '\n' + JSON.stringify(privateBody));

    // TODO verify selection, current > max (in case CSS does not work fully), overlapping games
    // TODO send
    // TODO refresh page after sending? or just remove selection add show comment?
}

function forEachRound(registrations, callee) {
    const rounds = getRounds();
    const games = getGames();
    Object.keys(rounds).forEach(roundId => {
        const round = rounds[roundId];
        const game = games[round.gameId];
        const playersMax = game.playersMax;
        const playersCurrent = registrations.filter(registration => {
            return registration.publicBody.roundId === roundId;
        }).length;
        callee(roundId, round, game, playersMax, playersCurrent);
    });
}
