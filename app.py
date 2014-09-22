# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os
import logging

import redis

from flask import Flask, request, jsonify
from flask.views import View
from rq import Queue, use_connection

from bandwidth_sdk import (Call, Event, Bridge)

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
# app.config.from_object('config')
CALLER = os.environ.get('CALLER_NUMBER')
BRIDGE_CALLEE = os.environ.get('BRIDGE_CALLEE')

DOMAIN = os.environ.get('DOMAIN')

APP_CALL_URL = 'http://{}{}'.format(DOMAIN, '/events')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level='DEBUG', format="%(levelname)s [%(name)s:%(lineno)s] %(message)s")

redis_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)
use_connection(conn)
# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return 'Its works'


class EventsHandler(View):
    methods = ['POST']
    event = None

    def dispatch_request(self):
        try:
            self.event = Event.create(**request.get_json())
        except Exception:
            return 'Malformed event', 400
        logger.debug(self.event)
        handler = getattr(self, self.event.event_type, self.not_implemented)
        return handler()

    def not_implemented(self):
        return '', 200


class CallEvents(EventsHandler):

    def async(self, func, *args, **kwargs):
        q = Queue('default')
        params = kwargs.pop('params', {})
        return q.enqueue_call(func, args, kwargs, **params)

    def answer(self):
        call = self.event.call
        self.async(call.speak_sentence,
                   'Hello from test application, press 1 to continue, '
                   'we want to make sure that you are a human', gender='female', tag='human_validation')
        return ''

    def dtmf(self):
        call = self.event.call
        if self.event.dtmf_digit == '1':
            self.async(call.speak_sentence,
                       'Thank you.', gender='female', tag='greeting_done')
        else:
            self.async(call.speak_sentence,
                       'We are sorry your input is not valid. The call will be terminated',
                       gender='female', tag='terminating')
        return ''

    def speak(self):
        event = self.event
        if not event.done:
            return ''
        call = self.event.call
        if event.tag == 'greeting_done':
            logger.debug('Starting dtmf gathering')
            self.async(call.gather.create,
                       max_digits='5',
                       terminating_digits='*',
                       inter_digit_timeout='7',
                       prompt={'sentence': 'Please enter your 5 digit code', 'loop_enabled': True},
                       tag='gather_started')
        elif event.tag == 'gather_complete':
            self.async(Call.create,
                       CALLER,
                       BRIDGE_CALLEE,
                       callback_url='http://{}{}'.format(DOMAIN, '/events/bridged'),
                       tag='other-leg:{}'.format(call.call_id))
        elif event.tag == 'terminating':
            self.async(call.hangup)
        return ''

    def gather(self):
        future = self.async(self.event.gather.stop)
        self.async(self.event.call.speak_sentence,
                   'Thank you, your input was {}, this call will be bridged'.format(self.event.digits),
                   gender='male',
                   tag='gather_complete',
                   params={'depends_on': future})
        return ''

    def hangup(self):
        # Creating cdr
        return ''


class BridgedLegEvents(EventsHandler):

    def async(self, func, args=None, kwargs=None, **params):
        q = Queue('default')
        return q.enqueue_call(func, args, kwargs, **params)

    def answer(self):
        """
        :return:
        """
        other_call_id = self.event.tag.split(':')[-1]
        self.async(Bridge.create,
                   self.event.call,
                   Call(other_call_id))
        return ''

    def hangup(self):
        """
        :return:
        """
        other_call_id = self.event.tag.split(':')[-1]
        if self.event.cause == "CALL_REJECTED":
            self.async(Call(other_call_id).speak_sentence,
                       'We are sorry, the user is reject your call',
                       gender='female',
                       tag='terminating')
        else:
            self.async(Call(other_call_id).hangup)
        return ''


app.add_url_rule('/events', view_func=CallEvents.as_view('call_events'))
app.add_url_rule('/events/bridged', view_func=BridgedLegEvents.as_view('bridged_call_events'))


@app.route('/start/call', methods=['POST'])
def start_call():
    inc = request.get_json()
    callee = inc.get('to')
    if not callee:
        return jsonify({'message': 'number field is required'}), 400
    Call.create(CALLER, callee, recording_enabled=False, callback_url=APP_CALL_URL)
    return jsonify({}), 201


# Error handlers.
# @app.errorhandler(500)
# def internal_error(error):
#     return 'error occurred', 500


@app.errorhandler(404)
def not_found_error(error):
    return 'Not found', 404

# ----------------------------------------------------------------------------#
# Delayed jobs
# ----------------------------------------------------------------------------#

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True)
