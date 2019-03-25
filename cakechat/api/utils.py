import json

from flask import jsonify


def get_api_error_response(message, code, logger):
    logger.error(message)
    return jsonify({'message': message}), code


def _is_list_of_unicode_strings(data):
    return bool(data and isinstance(data, (list, tuple)) and all(isinstance(s, str) for s in data))


def parse_dataset_param(params, param_name, required=True):
    if not required and params.get(param_name) is None:
        return None

    dataset = params[param_name]
    if not _is_list_of_unicode_strings(dataset):
        raise ValueError('`{}` should be non-empty list of unicode strings'.format(param_name))
    if not all(dataset):
        raise ValueError('`{}` should not contain empty strings'.format(param_name))

    return dataset


def perform_json_endpoint_request(flask_app, endpoint_function, data, endpoint_params=None, endpoint_method='POST'):
    """
    Perform request on a given endpoint inside the Flask app

    :param flask_app: Flask app
    :param endpoint_function: Endpoint function
    :param data: Data to pass as JSON payload
    :param endpoint_params: Params to fill placeholders in the endpoint
    :param endpoint_method: Http method name for passed endpoint
    :return: JSON response and status code
    """

    def perform_inner_request(flask_app, path, method, body, content_type):
        with flask_app.app_context():
            with flask_app.test_request_context(path=path, method=method, content_type=content_type, data=body):
                return flask_app.full_dispatch_request()

    def get_path_by_endpoint_function(app, endpoint_function, endpoint_params=None):
        for rule in app.url_map.iter_rules():
            if app.view_functions[rule.endpoint] == endpoint_function:
                _, path = rule.build(values=endpoint_params or {})
                return path

        raise Exception('Path for endpoint handler {} not found.'.format(endpoint_function))

    path = get_path_by_endpoint_function(flask_app, endpoint_function, endpoint_params)
    body = json.dumps(data)
    response = perform_inner_request(
        flask_app=flask_app, path=path, method=endpoint_method, content_type='application/json', body=body)

    try:
        response_data = json.loads(response.get_data().decode())
    except ValueError:
        response_data = None

    return response_data, response.status_code


def validate_json_endpoint(flask_app,
                           endpoint_function,
                           input_data,
                           output_validator,
                           endpoint_params=None,
                           endpoint_method='POST'):
    response, code = perform_json_endpoint_request(flask_app, endpoint_function, input_data, endpoint_params,
                                                   endpoint_method)

    if not output_validator(response, code):
        raise Exception('Validation failed for endpoint response "{}"'.format(response))
