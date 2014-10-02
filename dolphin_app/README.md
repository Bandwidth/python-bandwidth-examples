# Dolphin app

Simple Flask application for handling calls usage  [bandwidth python sdk](https://github.com/bandwidthcom/python-bandwidth).


## Getting started
You need to have

    - Git
    - Python (2.7, 3.3, 3.4)
    - Bandwidth Application Platform account
    - pip
    - Heroku account and installed heroku Heroku Toolbelt


## Setup

1. Clone the repository:

        git clone https://github.com/bandwidthcom/python-bandwidth-examples.git

        cd python-bandwidth-examples/dolphin_app

2. Allocate new phone number in Bandwidth resource:

    2.1. Setup client sdk instance with your Catapult credentials:

        >>> from bandwidth_sdk import Client
        >>> Client('u-user', 't-token', 's-secret')

    2.2. Lookup for available number:

        >>> from bandwidth_sdk import AvailableNumber
        >>> available_numbers = AvailableNumber.list_local(city='San Francisco', state='CA')
        >>> available_numbers[0].allocate()
        PhoneNumber(number=+14158000000)

    This is yours allocated phonenumber, we will use this number in next steps.

    2.3 Also, you need to upload `dolphin.mp3` into yours media resources, for correct work of this example (This file existing in current directory).

        >>> from bandwidth_sdk import Media
        >>> Media('dolphin').upload('dolphin.mp3', file_path='dolphin.mp3')


3. Create new heroku application:

        heroku apps:create
        > Created http://your-app.herokuapp.com/ | git@heroku.com:your-app.git

4. Set up heroku environment variables:

    Bandwidth credentials tier:

        heroku config:set BANDWIDTH_USER_ID=u-user-id
        heroku config:set BANDWIDTH_SECRET=s-secret
        heroku config:set BANDWIDTH_TOKEN=t-token

    Web app tier:

        heroku config:set BRIDGE_CALLEE=+YOUR-NUMBER
        heroku config:set CALLER_NUMBER=+ALOCATED-NUMBER
        heroku config:set DOMAIN=your-app.herokuapp.com

##  Deploy

Push code to heroku:

    git remote add heroku git@heroku.com:your-app.git

    git push heroku master:master

Make sure that all went well:

    heroku logs -t

## Demo

Start incoming call from command line:

    curl -d '{"to": "+YOUR-NUMBER"}' http://your-app.herokuapp.com/start/demo --header "Content-Type:application/json"

It will:

1. Speak sentence "hello flipper" - on answer of the incoming call
2. Play audio dolphin.mp3
3. Play ("Press 1 to connect with your fish, press 2 to disconnect") and wait for dtmf event
4. On receiving ("1"), connect to a number (make this easy to change). Let the incoming call know you're connecting to the fish
5. On answer (outgoing leg), whisper ('you have a dolphin on the line').
6. Create a new call from bandwidth number to $BRIDGE_CALLEE and bridge it with yours.
