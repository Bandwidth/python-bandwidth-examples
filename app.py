# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os
import logging

from flask import Flask, request, jsonify

from bandwidth_sdk import (Call, Event, Bridge, AnswerCallEvent,
                           PlaybackCallEvent, HangupCallEvent,
                           GatherCallEvent, SpeakCallEvent)

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
# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return 'Its works'


@app.route('/start/call', methods=['POST'])
def start_call():
    inc = request.get_json()
    callee = inc.get('to')
    if not callee:
        return jsonify({'message': 'number field is required'}), 400
    Call.create(CALLER, callee, recording_enabled=False, callback_url=APP_CALL_URL)
    return jsonify({}), 201


@app.route('/events', methods=['POST'])
def handle_event():
    event = Event.create(**request.get_json())
    call = event.call
    logger.debug('Input> : %s', request.get_json())
    logger.debug('Processing %s', event)
    logger.debug('In dict: %s', vars(event))
    if isinstance(event, AnswerCallEvent):
        if not event.tag:
            # Call have just started
            call.speak_sentence('Hello from test application', gender='female', tag='greeting')

    elif isinstance(event, SpeakCallEvent):
        logger.debug('Speak event received')
        if event.done:
            if event.tag == 'greeting':
                logger.debug('Starting dtmf gathering')
                call.gather.create(max_digits='5',
                                   terminating_digits='*',
                                   inter_digit_timeout='7',
                                   prompt={'sentence': 'Please enter your 5 digit code', 'loop_enabled': True},
                                   tag='gather_started')
            elif event.tag == 'gather_complete':
                Call.create(CALLER, BRIDGE_CALLEE,
                            callback_url='http://{}{}'.format(DOMAIN, '/events/bridged'),
                            tag='other-leg:{}'.format(call.call_id))
            elif event.tag == 'terminating':
                call.hangup()

    elif isinstance(event, GatherCallEvent):
        event.gather.stop()
        call.speak_sentence('Thank you, your input was {}, this call will be bridged'.format(event.digits),
                            gender='male',
                            tag='gather_complete')
        # if event.digits:
        #     call.speak_sentence('Thank you, your input was {}, this call will be bridged'.format(event.digits),
        #                         gender='male',
        #                         tag='gather_complete')
        # else:
        #     call.speak_sentence('We are sorry your input is not valid. The call will be terminated',
        #                         gender='female', tag='terminating')

    elif isinstance(event, HangupCallEvent):
        logger.debug('Call ended')
    else:
        logger.debug('Skipping %s', event)
    return '', 200


@app.route('/events/bridged', methods=['POST'])
def handle_bridged_leg():
    event = Event.create(**request.get_json())
    call = event.call
    if isinstance(event, AnswerCallEvent):
        other_call_id = event.tag.split(':')[-1]
        Bridge.create(call, Call(other_call_id))
    elif isinstance(event, HangupCallEvent):
        other_call_id = event.tag.split(':')[-1]
        if event.cause == "CALL_REJECTED":
            Call(other_call_id).speak_sentence('We are sorry, the user is reject your call',
                                               gender='female',
                                               tag='terminating')
        else:
            Call(other_call_id).hangup()
    return '', 200


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
