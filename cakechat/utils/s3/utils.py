import json


def _create_metadata(model):
    model_params_str = json.dumps(model.model_params, indent=2, sort_keys=True)
    metrics_str = json.dumps(model.metrics, indent=2, sort_keys=True) if model.metrics else 'Unknown'
    metadata = 'Model params:\n\n{}\n\nValidation metrics:\n\n{}\n'.format(model_params_str, metrics_str)

    return metadata
