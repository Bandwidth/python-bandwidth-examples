# Dolphin app

Simple Flask application for handling calls using the [Bandwidth Python SDK](https://github.com/bandwidthcom/python-bandwidth).


## Getting started
You need to have

    - Git
    - Python (2.7, 3.3, 3.4)
    - Bandwidth Application Platform account
    - pip
    - Heroku account and installed Heroku Toolbelt
    - ngrok tool for local tests


## Setup

#### Clone the repository

```console
git clone https://github.com/bandwidthcom/python-bandwidth-examples.git
cd python-bandwidth-examples/dolphin_app
```
#### Allocate a new phone number in Bandwidth resource

Setup the Bandwidth Python SDK on your development environment
```console
cd /opt
sudo pip install -e git+https://github.com/bandwidthcom/python-bandwidth.git#egg=bandwidth_sdk
cd -
```
Note: This may have to be run as `root` or with the `--user` flag if you are not using python virtual environment.

Setup the client SDK environment with your Catapult credentials:
```console
export BANDWIDTH_USER_ID=<your-user-id>
export BANDWIDTH_API_TOKEN=<your-token>
export BANDWIDTH_API_SECRET=<your-secret>
```
or explicitly set up in the code/interpreter as an alternative way:

```python
from bandwidth_sdk import Client

Client('u-user', 'token', 'secret')
```

Note: if you going to follow this way you should uncomment [application.py:32](https://github.com/bandwidthcom/python-bandwidth-examples/blob/master/dolphin_app/application.py#L32) 
line and put your credential there.
You also be able to skip bandwidth credentials setup part in next steps.

Allocate a new number using the python interpreter:
```python
from bandwidth_sdk import PhoneNumber

available_numbers = PhoneNumber.list_local(city='San Francisco', state='CA')
available_numbers[0].allocate()
>>> PhoneNumber(number=+14158000000)
```
This is your allocated phone number, we will use this number in next steps.

Also, you will need to upload `dolphin.mp3` into your media resources for this example to work correctly (This file exists in the current directory).
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

##  Deploying to Heroku

#### Create a new Heroku application:
```console
heroku apps:create
> Created http://<your-app>.herokuapp.com/ | git@heroku.com:<your-app>.git
'''

You may also see:
'''
> Git remote heroku added
```
This means a git remote called Heroku was automatically added to your git repository.  If so you may skip the next step.

#### Add remote git repository
```console
git remote add heroku git@heroku.com:<your-app>.git
```

#### Setup the Heroku environment variables:

Bandwidth credentials:
```console
heroku config:set BANDWIDTH_USER_ID=$BANDWIDTH_USER_ID --app <your-app-name>
heroku config:set BANDWIDTH_API_TOKEN=$BANDWIDTH_API_TOKEN --app <your-app-name>
heroku config:set BANDWIDTH_API_SECRET=$BANDWIDTH_API_SECRET --app <your-app-name>
```

Web app settings:
```console
heroku config:set BRIDGE_CALLEE=<+your-number-for-call-lef#2> --app <your-app-name>
heroku config:set CALLER_NUMBER=<+your-allocated-number> --app <your-app-name>
heroku config:set DOMAIN=<your-app>.herokuapp.com --app <your-app-name>
```

Push code to Heroku:
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


## Demo

#### Check app configuration from the command line:
```console
curl http://<your-app>.herokuapp.com
```

You should see the following message
```
This app is ready to use
```
otherwise you need to check environment variables.


#### Start an incoming call:
```console
curl -d '{"to": "<+your-number-for-call-leg#1>"}' http://<your-app>.heroku.com/start/demo --header "Content-Type:application/json"
```

It will:

1. Create a call from $CALLER_NUMBER to the number specified on the command line.
2. Once connected play the audio in dolphin.mp3.
2. Play ("Press 1 to speak with the dolphin, 2 to let it go") in a loop, waiting for a DTMF event.
3. On receiving ("2") - Play ("This call will be terminated") and disconnect the call.
4. On receiving ("1") - Play ("You have a dolphin on line 1, watch out, he's hungry.") then create a new call from $CALLER_NUMBER to $BRIDGE_CALLEE number and bridge the call with the original call.


## Local Setup

#### Installing ngrok tool (For local tests):

Download [ngrok](https://ngrok.com/download).
```console
unzip /path/to/ngrok.zip
./ngrok http 5000
```

The ngrok will create a Forwarding DNS to your localhost. You will need the DNS to setup on environment variable.

#### Install python dependences
```console
sudo pip install redis
sudo pip install Flask
```

#### Setup local environment variables
```console
export BANDWIDTH_USER_ID=<your-user-id>
export BANDWIDTH_API_TOKEN=<your-token>
export BANDWIDTH_API_SECRET=<your-secret>
export BRIDGE_CALLEE=<+your-number-for-call-lef#2>
export CALLER_NUMBER=<+your-allocated-number>
export DOMAIN=<your-ngrok-forwarding-dns>
```

#### Initiate the application
```console
python app.py
```

Start incoming call from command line:
```console
curl -d '{"to": "<+your-number-for-call-leg#1>"}' http://<your-ngrok-forwarding-dns>/start/demo --header "Content-Type:application/json"
```
