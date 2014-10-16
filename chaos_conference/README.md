# Uber Conference

Simple Flask application for handling conference calls usage  [bandwidth python sdk](https://github.com/bandwidthcom/python-bandwidth).


## Getting started
You need to have

    - Git
    - Python (2.7, 3.3, 3.4)
    - Bandwidth Application Platform account
    - pip
    - Heroku account and installed heroku Heroku Toolbelt


## Setup

#### Clone the repository

```console
git clone https://github.com/bandwidthcom/python-bandwidth-examples.git
cd python-bandwidth-examples/uber_conference
```
#### Allocate new phone number in Bandwidth resource

Set up bandwidth sdk on local machine
```console
pip install -e git+https://github.com/bandwidthcom/python-bandwidth.git#egg=bandwidth_sdk
```
Note: This may have to be run as `root` or with `--user` flag if you are not using python virtual environment.


Setup client sdk instance with your Catapult credentials:
```console
export BANDWIDTH_USER_ID=u-your-user-id
export BANDWIDTH_API_TOKEN=t-your-token
export BANDWIDTH_API_SECRET=s-your-secret
```
Lookup for available number using python interpreter:
```python
>>> from bandwidth_sdk import AvailableNumber
>>> available_numbers = AvailableNumber.list_local(city='San Francisco', state='CA')
>>> available_numbers[0].allocate()
PhoneNumber(number=+14158000000)
```
This number will host the conference. We will use it in next steps.

Also, you need to upload `dolphin.mp3` into yours media resources, for correct work of this example (This file existing in current directory).
```python
>>> from bandwidth_sdk import Media
>>> Media.upload('dolphin.mp3', file_path='dolphin.mp3')
```

#### Create new heroku application:
```console
heroku apps:create
> Created http://your-app.herokuapp.com/ | git@heroku.com:your-app.git
```
#### Set up heroku environment variables:

Bandwidth credentials tier:
```console
heroku config:set BANDWIDTH_USER_ID=u-user-id
heroku config:set BANDWIDTH_API_TOKEN=t-token
heroku config:set BANDWIDTH_API_SECRET=s-secret
```
Web app tier:
```console
heroku config:set CONFERENCE_NUMBER=+ALLOCATED-NUMBER
heroku config:set DOMAIN=your-app.herokuapp.com
```
##  Deploy

Push code to heroku:
```console
git init
git add .
git commit -m "My app"
git remote add heroku git@heroku.com:your-app.git
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
curl -d '{"to": "+YOUR-NUMBER"}' http://your-app.herokuapp.com/start/demo --header "Content-Type:application/json"
```

It will:
    TBD