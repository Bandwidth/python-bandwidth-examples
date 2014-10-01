# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os
import logging

from flask import Flask, request, jsonify, url_for
from flask.views import View

from bandwidth_sdk import (Call, Event, Bridge)

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)


CALLER = os.getenv('CALLER_NUMBER')

BRIDGE_CALLEE = os.getenv('BRIDGE_CALLEE')

DOMAIN = os.getenv('DOMAIN')

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

logging.basicConfig(level='DEBUG', format="%(levelname)s [%(name)s:%(lineno)s] %(message)s")

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return 'Its works'


@app.route('/start/demo', methods=['POST'])
def start_demo():
    """
    Start point
    """
    inc = request.get_json()
    callee = inc.get('to')
    if not callee:
        return jsonify({'message': 'number field is required'}), 400
    callback_url = 'http://{}{}'.format(DOMAIN, url_for('demo_call_events'))
    Call.create(CALLER, callee, recording_enabled=False, callback_url=callback_url)
    return jsonify({}), 201


class EventsHandler(View):
    methods = ['POST']
    event = None

    def dispatch_request(self):
        try:
            self.event = Event.create(**request.get_json())
        except Exception:
            return jsonify({'message': 'Malformed event'}), 400
        logger.debug(self.event)
        handler = getattr(self, self.event.event_type, self.not_implemented)
        return handler()

    def not_implemented(self):
        return '', 200


class DemoEvents(EventsHandler):

    def answer(self):
        call = self.event.call
        call.speak_sentence('hello flipper', gender='female', tag='hello-state')
        return ''

    def speak(self):
        event = self.event
        if not event.done:
            return ''
        call = self.event.call
        if event.tag == 'gather_complete':
            Call.create(CALLER,
                        BRIDGE_CALLEE,
                        callback_url='http://{}{}'.format(DOMAIN, url_for('bridged_call_events')),
                        tag='other-leg:{}'.format(call.call_id))
        elif event.tag == 'terminating':
            call.hangup()
        elif event.tag == 'hello-state':
            self.event.call.play_audio('dolphin.mp3', tag='dolphin-state')
        return ''

    def playback(self):
        event = self.event
        if not event.done and event.tag != 'dolphin-state':
            return ''
        event.call.gather.create(max_digits='5',
                                 terminating_digits='*',
                                 inter_digit_timeout='7',
                                 prompt={'sentence': 'Press 1 to connect with your fish, press 2 to disconnect',
                                         'loop_enabled': True},
                                 tag='gather_started')

    def gather(self):
        self.event.gather.stop()
        if self.event.digits == '1':
            self.event.call.speak_sentence(
                'Thank you, your input was {}, this call will be bridged'.format(self.event.digits),
                gender='male',
                tag='gather_complete')
        else:
            self.event.call.speak_sentence('Invalid input, this call will be terminated',
                                           gender='male',
                                           tag='terminating')
        return ''

    def hangup(self):
        # Creating cdr
        return ''


class BridgedLegEvents(EventsHandler):

    def answer(self):
        other_call_id = self.event.tag.split(':')[-1]
        Bridge.create(self.event.call, Call(other_call_id))
        return ''

    def hangup(self):
        other_call_id = self.event.tag.split(':')[-1]
        if self.event.cause == "CALL_REJECTED":
            Call(other_call_id).speak_sentence('We are sorry, the user is reject your call',
                                               gender='female',
                                               tag='terminating')
        else:
            Call(other_call_id).hangup()
        return ''


app.add_url_rule('/events/bridged', view_func=BridgedLegEvents.as_view('bridged_call_events'))
app.add_url_rule('/events/demo', view_func=DemoEvents.as_view('demo_call_events'))


# Error handlers.
# @app.errorhandler(500)
# def internal_error(error):
#     return 'error occurred', 500


@app.errorhandler(404)
def not_found_error(error):
    return 'Not found', 404


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True)
