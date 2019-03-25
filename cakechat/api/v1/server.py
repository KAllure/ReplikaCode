from flask import Flask, request, jsonify

from cakechat.api.response import get_response
from cakechat.api.utils import get_api_error_response, parse_dataset_param, validate_json_endpoint
from cakechat.config import EMOTIONS_TYPES, DEFAULT_CONDITION
from cakechat.utils.logger import get_logger

_logger = get_logger(__name__)

app = Flask(__name__)


@app.route('/cakechat_api/v1/healthcheck', methods=['GET'])
def healthcheck():
    validate_json_endpoint(
        flask_app=app,
        endpoint_function=get_model_response,
        input_data={'context': ['hi', 'how r u doin', 'are you ok?']},
        output_validator=lambda response, code: ('response' in response) and (code == 200))

    return '', 200


@app.route('/cakechat_api/v1/actions/get_response', methods=['POST'])
def get_model_response():
    params = request.get_json()
    _logger.info('request params: {}'.format(params))

    try:
        dialog_context = parse_dataset_param(params, param_name='context')
    except KeyError as e:
        return get_api_error_response('Malformed request, no "{}" param was found'.format(str(e)), 400, _logger)
    except ValueError as e:
        return get_api_error_response('Malformed request: {}'.format(str(e)), 400, _logger)

    emotion = params.get('emotion', DEFAULT_CONDITION)
    if emotion not in EMOTIONS_TYPES:
        return get_api_error_response(
            'Malformed request, emotion param "{}" is not in emotion list {}'.format(emotion, list(EMOTIONS_TYPES)),
            400, _logger)

    response = get_response(dialog_context, emotion)
    _logger.info('Given response: "{}" for context: {}; emotion "{}"'.format(response, dialog_context, emotion))

    return jsonify({'response': response}), 200


@app.errorhandler(Exception)
def on_exception(exception):
    return get_api_error_response('Can\'t process request: {}'.format(exception), 500, _logger)
