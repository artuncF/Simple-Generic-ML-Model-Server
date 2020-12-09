from src.load_model import load_model_from_file
from src.load_config import get_config
from flask_api import status
from flask import Flask, request
import logging.config
import os
app = Flask(__name__)

models = {}

cfg = get_config()
logging.config.dictConfig(cfg['logging'])
log = logging.getLogger(__name__)


def get_model_name_from_path(file_path):
    name_with_ext = os.path.basename(os.path.normpath(file_path))
    return os.path.splitext(name_with_ext)[0]


def load_callback(file_path):
    try:
        model = load_model_from_file(file_path)
        model_name = get_model_name_from_path(file_path)
        models.update({model_name: model})
        return True
    except Exception as e:
        log.debug(e)
        return False


def unload_callback(file):
    try:
        models.pop(file)
        return True
    except Exception as e:
        log.debug(e)
        return False


def predict_callback(json_data):
    model_name = json_data.pop('model_name')
    if models[model_name] is None:
        log.info(f"Model with name {model_name} does not exist.")
        return ''
    log.error(f"Model input names: {models[model_name].inputNames}")
    predict_event = {"columns": list(json_data.keys()), "data": [
        list(json_data.values())]}
    log.error(predict_event)
    probs = list(models[model_name].predict(predict_event))
    max_prob_index = probs.index(max(probs))
    return models[model_name].outputNames[max_prob_index]


@app.route('/health', methods=['POST'])
def app_status():
    return f"{status.HTTP_200_OK}"


@app.route('/load', methods=['POST'])
def load_model():
    file_path = request.data.decode("utf-8")
    is_load_ok = load_callback(file_path)
    return f"{status.HTTP_200_OK}" if is_load_ok else f"{status.HTTP_500_INTERNAL_SERVER_ERROR}"


@app.route('/unload', methods=['POST'])
def unload_model():
    file_path = request.data.decode("utf-8")
    is_unload_ok = unload_callback(file_path)
    return f"{status.HTTP_200_OK}" if is_unload_ok else f"{status.HTTP_500_INTERNAL_SERVER_ERROR}"


@app.route("/predict", methods=['POST'])
def predict():
    json_data = request.get_json()
    prediction = predict_callback(json_data)
    return f'{prediction}'


@app.route("/info", methods=['GET'])
def get_models_info():
    models_info = {}
    for model_name, model in models.items():
        print(model.targetFields)
        models_info.update({
            model_name: {
                'features': model.inputNames,
                'outputs': model.outputNames
            }
        })
    return models_info


if __name__ == "__main__":
    app.run(debug=cfg['app']['debug'], port=cfg['app']['port'])
