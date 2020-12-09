import confuse
from os.path import dirname, abspath, join
from pathlib import Path


FILE_DIR = dirname(abspath(__file__))
ROOT_DIR = Path(FILE_DIR).parent
CONFIG_DIR = join(ROOT_DIR, 'config')
CONFIG_PATH = join(CONFIG_DIR, 'conf.yaml')


class ModelServerAppConf(confuse.Configuration):
    def config_dir(self):
        return CONFIG_DIR


def get_config():
    cfg = ModelServerAppConf("python-model-server")
    return cfg.get()
