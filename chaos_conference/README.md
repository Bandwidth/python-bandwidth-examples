# Chaos Conference

Simple Flask application for handling conference calls using [Bandwidth Python SDK](https://github.com/bandwidthcom/python-bandwidth).


## Getting started
You need to have

    - Git
    - Python (2.7, 3.3, 3.4)
    - Bandwidth Application Platform account
    - pip
    - Heroku account and Heroku Toolbelt installed
    - ngrok for local tests


## Setup

#### Clone the repository

```console
git clone https://github.com/bandwidthcom/python-bandwidth-examples.git
cd python-bandwidth-examples/chaos_conference
```
#### Allocate new phone number in Bandwidth resource

Set up Bandwidth SDK on local machine
```console
cd /opt
sudo pip install -e git+https://github.com/bandwidthcom/python-bandwidth.git#egg=bandwidth_sdk
cd -
```
Note: This may have to be run as `root` or with `--user` flag if you are not using python virtual environment.


Setup client SDK instance with your Catapult credentials:
```console
export BANDWIDTH_USER_ID=<your-user-id>
export BANDWIDTH_API_TOKEN=<your-token>
export BANDWIDTH_API_SECRET=<your-secret>
```
Lookup for available number using python interpreter:
```python
>>> from bandwidth_sdk import PhoneNumber
>>> available_numbers = PhoneNumber.list_local(city='San Francisco', state='CA')
>>> available_numbers[0].allocate()
PhoneNumber(number=+14158000000)
```
Now you have an allocated number that will host the conference. We will use it in next steps.

#### Create new Heroku application:
```console
heroku apps:create
> Created http://<your-app-name>.herokuapp.com/ | git@heroku.com:<your-app-name>.git
```
#### Setup Heroku environment variables:

Bandwidth credentials tier:
```console
heroku config:set BANDWIDTH_USER_ID=<your-user-id> --app <your-heroku-app-name>
heroku config:set BANDWIDTH_API_TOKEN=<your-token> --app <your-heroku-app-name>
heroku config:set BANDWIDTH_API_SECRET=<your-secret> --app <your-heroku-app-name>
```
Web app tier:
```console
heroku config:set CONFERENCE_NUMBER=<+your-allocated-nuymber> --app <your-heroku-app-name>
heroku config:set DOMAIN=<your-app-name>.herokuapp.com --app <your-heroku-app-name>
```
##  Deploy

Push code to heroku:
```console
git init
git add .
git commit -m "My app"
git remote add heroku git@heroku.com:<your-app-name>.git
git push heroku master:master
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

Start incoming call from command line:
```console
curl -d '{"to": "+YOUR-NUMBER"}' http://<your-app>.herokuapp.com/start/demo --header "Content-Type:application/json"
```

It will:

1. Create a call to "YOUR-NUMBER".
2. Place your call in a conference hosted by the "CONFERENCE_NUMBER".
3. Play an audio to inform that you are the first member in the conference.




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
export DOMAIN=<your-ngrok-forwarding-dns>
export CONFERENCE_NUMBER=<+your-allocated-nuymber>
```

#### Initiate the application
```console
python app.py
```

Start incoming call from command line:
```console
curl -d '{"to": "+YOUR-NUMBER"}' http://<your-ngrok-forwarding-dns>/start/demo --header "Content-Type:application/json"
```
