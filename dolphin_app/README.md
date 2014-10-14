# Dolphin app

Simple Flask application for handling calls usage  [bandwidth python sdk](https://github.com/bandwidthcom/python-bandwidth).


## Getting started
You need to have

    - Git
    - Python (2.7, 3.3, 3.4)
    - Bandwidth Application Platform account
    - pip
    - Heroku account and installed Heroku Toolbelt
      or
      AWS account and installed AWS Elastic Beanstalk Command Line Tool.


## Setup

#### Clone the repository

```console
git clone https://github.com/bandwidthcom/python-bandwidth-examples.git
cd python-bandwidth-examples/dolphin_app
```
#### Allocate new phone number in Bandwidth resource

Set up bandwidth sdk on local machine
```console
pip install -e git+https://github.com/bandwidthcom/python-bandwidth.git#egg=bandwidth_sdk
```
Note: This may have to be run as `root` or with `--user` flag if you are not using python virtual environment.

Setup client sdk instance with your Catapult credentials:
```console
export BANDWIDTH_USER_ID='u-your-user-id'
export BANDWIDTH_API_TOKEN='t-your-token'
export BANDWIDTH_API_SECRET='s-your-secret'
```
Lookup for available number using python interpreter:
```python
from bandwidth_sdk import AvailableNumber

available_numbers = AvailableNumber.list_local(city='San Francisco', state='CA')
available_numbers[0].allocate()
>>> PhoneNumber(number=+14158000000)
```
This is yours allocated phone number, we will use this number in next steps.

Also, you need to upload `dolphin.mp3` into yours media resources, for correct work of this example (This file existing in current directory).
```python
from bandwidth_sdk import Media

Media.upload('dolphin.mp3', file_path='dolphin.mp3')
```

#### Initialize git
```console
git init
git add .
git commit -m "My app"
```

##  Deploying to heroku


#### Create new heroku application:
```console
heroku apps:create
> Created http://your-app.herokuapp.com/ | git@heroku.com:your-app.git
```

#### Add remote git repository
```console
git remote add heroku git@heroku.com:your-app.git
```

#### Set up heroku environment variables:

Bandwidth credentials tier:
```console
heroku config:set BANDWIDTH_USER_ID=$BANDWIDTH_USER_ID
heroku config:set BANDWIDTH_API_TOKEN=$BANDWIDTH_API_TOKEN
heroku config:set BANDWIDTH_API_SECRET=$BANDWIDTH_API_SECRET
```
Web app tier:
```console
heroku config:set BRIDGE_CALLEE=+YOUR-NUMBER-FOR-CALL-LEG#2
heroku config:set CALLER_NUMBER=+ALLOCATED-NUMBER
heroku config:set DOMAIN=your-app.herokuapp.com
```

Push code to heroku:
```console
git push heroku master
```

Add a web dyno
```console
heroku ps:scale web=1
```

Make sure that all went well:
```console
heroku logs -t
```

##  Deploying to  AWS

You will need an AWS account with access to the  [AWS Elastic Beanstalk](http://aws.amazon.com/elasticbeanstalk)

We really recommend to follow [Deploying a Flask Application to AWS Elastic Beanstalk](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_Python_flask.html) instructions.

Additionally you need to set up environment variables:

```console
BANDWIDTH_USER_ID=your-id
BANDWIDTH_API_TOKEN=your-token
BANDWIDTH_API_SECRET=your-secret
BRIDGE_CALLEE=+YOUR-NUMBER-FOR-CALL-LEG#2
CALLER_NUMBER=+ALLOCATED-NUMBER
DOMAIN=your-application-domain.com
```

## Demo

Start incoming call from command line:
```console
curl -d '{"to": "+YOUR-NUMBER-FOR-CALL-LEG#1"}' http://your-app.com/start/demo --header "Content-Type:application/json"
```

It will:

1. Speak sentence "hello flipper" - on answer of the incoming call
2. Play audio dolphin.mp3
3. Play ("Press 1 to connect with your fish, press 2 to disconnect") and wait for dtmf event
4. On receiving ("1"), connect to a number (make this easy to change). Let the incoming call know you're connecting to the fish
5. On answer (outgoing leg), whisper ('you have a dolphin on the line').
6. Create a new call from bandwidth number to $BRIDGE_CALLEE and bridge it with yours.
