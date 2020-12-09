from pypmml import Model


def load_model_from_file(path):
    return Model.load(path)
