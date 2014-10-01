# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os
import logging

from flask import Flask, request, jsonify, url_for
from flask.views import View

from bandwidth_sdk import (Call, Event, Bridge, Media)

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
    ready_to_use = all((BRIDGE_CALLEE, DOMAIN, CALLER))
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
    callback_url = 'http://{}{}'.format(DOMAIN, url_for('demo_call_events'))
    Call.create(CALLER, callee, recording_enabled=False, callback_url=callback_url)
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
        handler = getattr(self, self.event.event_type, self.not_implemented)
        return handler()

    def not_implemented(self):
        return jsonify({}), 200


class DemoEvents(EventsHandler):

    def answer(self):
        call = self.event.call
        call.speak_sentence('hello flipper', gender='female', tag='hello-state')
        return jsonify({})

    def speak(self):
        event = self.event
        if not event.done:
            return jsonify({})
        call = self.event.call
        if event.tag == 'gather_complete':
            Call.create(CALLER,
                        BRIDGE_CALLEE,
                        callback_url='http://{}{}'.format(DOMAIN, url_for('bridged_call_events')),
                        tag='other-leg:{}'.format(call.call_id))
        elif event.tag == 'terminating':
            call.hangup()
        elif event.tag == 'hello-state':
            # find the dolhin.mp3  media
            medias = [m for m in Media.list() if m.media_name == 'dolphin.mp3']
            if medias:
                call.play_audio(medias[0].media_url, tag='dolphin-state')
            else:
                call.speak_sentence('We are sorry, media resource dolphin.mp3 is not found', tag='terminating')
        return jsonify({})

    def playback(self):
        event = self.event
        if event.tag == 'dolphin-state' and event.done:
            event.call.gather.create(max_digits='5',
                                     terminating_digits='*',
                                     inter_digit_timeout='7',
                                     prompt={'sentence': 'Press 1 to connect with your fish, press 2 to disconnect',
                                             'loop_enabled': True},
                                     tag='gather_started')
        return jsonify({})

    def gather(self):
        if self.event.tag != 'gather_started':
            return jsonify({})

        if self.event.digits.startswith('1'):
            self.event.call.speak_sentence(
                'Thank you, your input was {}, this call will be bridged'.format(self.event.digits),
                gender='male',
                tag='gather_complete')
        else:
            self.event.call.speak_sentence('Invalid input, this call will be terminated',
                                           gender='male',
                                           tag='terminating')
        return jsonify({})

    def hangup(self):
        # Creating cdr
        return jsonify({})


class BridgedLegEvents(EventsHandler):

    def answer(self):
        other_call_id = self.event.tag.split(':')[-1]
        Bridge.create(self.event.call, Call(other_call_id))
        return jsonify({})

    def hangup(self):
        other_call_id = self.event.tag.split(':')[-1]
        if self.event.cause == "CALL_REJECTED":
            Call(other_call_id).speak_sentence('We are sorry, the user is reject your call',
                                               gender='female',
                                               tag='terminating')
        else:
            Call(other_call_id).hangup()
        return jsonify({})


app.add_url_rule('/events/bridged', view_func=BridgedLegEvents.as_view('bridged_call_events'))
app.add_url_rule('/events/demo', view_func=DemoEvents.as_view('demo_call_events'))


@app.errorhandler(404)
def not_found_error(error):
    return 'Not found', 404


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run()
