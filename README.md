# Dolphin app

Simple Flask application for handling calls using  [bandwidth python sdk](https://github.com/bandwidthcom/python-bandwidth).


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

        cd  python-bandwidth-examples

2. Allocate new phone number in Bandwidth resource:

        TBD

        Upload dolphin.mp3

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
3. Dtmf gather ("Press 1 to connect with your fish, press 2 to disconnect")
4. On gather("1"), connect to a number (make this easy to change). Let the incoming call know you're connecting to the fish")
5. On answer (outgoing leg), whisper ('you have a dolphin on the line').
6. Create a new call from bandwidth number to $BRIDGE_CALLEE and bridge it with yours.
