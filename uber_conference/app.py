# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os
import logging
from redis import Redis

from flask import Flask, request, jsonify, url_for
from flask.views import View

from bandwidth_sdk import (Call, Event, Conference)

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)


CONFERENCE_NUMBER = os.getenv('CONFERENCE_NUMBER')

REDISCLOUD_URL = os.getenv('REDISCLOUD_URL', 'redis://127.0.0.1:6379')

DOMAIN = os.getenv('DOMAIN')

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

logging.basicConfig(level='DEBUG', format="%(levelname)s [%(name)s:%(lineno)s] %(message)s")

redis = Redis.from_url(REDISCLOUD_URL)

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    ready_to_use = all((DOMAIN, CONFERENCE_NUMBER))
    return 'This app is ready to use' if ready_to_use else 'Please set up environment variables for the app'


@app.route('/start/demo', methods=['POST'])
def start_demo():
    """
    Start point
    """
    inc = request.get_json()
    callee = inc.get('to')
    if not callee:
        return jsonify({'message': 'number field is required'}), 400
    callback_url = 'http://{}{}'.format(DOMAIN, url_for('first_member_events'))

    Call.create(CONFERENCE_NUMBER, callee,
                recording_enabled=False,
                callback_url=callback_url,
                )
    return jsonify({}), 201


class EventsHandler(View):
    methods = ['POST']
    event = None

    def dispatch_request(self):
        try:
            data = request.get_json()
            logger.debug('Event json: %s', data)
            self.event = Event.create(**data)
        except Exception:
            return jsonify({'message': 'Malformed event'}), 400
        logger.debug(self.event)
        handler = getattr(self, self.event.event_type.replace('-', '_'), self.not_implemented)
        return handler()

    def not_implemented(self):
        return jsonify({}), 200


class FirstMemberHandler(EventsHandler):

    def answer(self):
        call = self.event.call
        call.speak_sentence('Hello! You will be first member of conference', voice='Kate')
        return jsonify({})

    def speak(self):
        event = self.event
        if not event.done:
            # ignore start speak events
            return jsonify({})
        call = self.event.call
        conference_url = 'http://{}{}'.format(DOMAIN, url_for('conference_call_events'))
        conference = Conference.create(from_=CONFERENCE_NUMBER, callback_url=conference_url)
        conference.add_member(call.call_id, join_tone=True, leaving_tone=True)
        return jsonify({})


class CallHandler(EventsHandler):

    def answer(self):
        call = self.event.call
        conference_id = redis.get('active-conf-{}'.format(self.event.to))
        if conference_id:
            call.speak_sentence('You will be join to conference.',
                                voice='Kate',
                                tag='conference:{}'.format(conference_id))
        else:
            call.speak_sentence('We are sorry, the conference is not active.', voice='Kate', tag='terminating')
        return jsonify({})

    def speak(self):
        event = self.event
        if not event.done:
            # ignore start speak events
            return jsonify({})
        call = self.event.call
        if event.tag == 'terminating':
            call.hangup()
        else:
            conference_id = event.tag.split(':')[-1]
            conference = Conference(conference_id)
            conference.add_member(call.call_id, join_tone=True)
        return jsonify({})


class ConferenceHandler(EventsHandler):

    def conference(self):
        conference = self.event.conference
        if self.event.status == 'started':
            redis.set('active-conf-{}'.format(conference.from_), conference.id)
            logger.debug('Conference was saved to redis.')
        elif self.event.status == 'done':
            redis.delete('active-conf-{}'.format(conference.from_))
            logger.debug('Conference was deleted from redis storage.')
        return jsonify({})

    def conference_member(self):
        return jsonify({})

    def conference_speak(self):
        return jsonify({})


app.add_url_rule('/events/first_member', view_func=FirstMemberHandler.as_view('first_member_events'))
app.add_url_rule('/events/other_call_events', view_func=CallHandler.as_view('demo_call_events'))
app.add_url_rule('/events/conference', view_func=ConferenceHandler.as_view('conference_call_events'))


@app.errorhandler(404)
def not_found_error(error):
    return 'Not found', 404


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run()
