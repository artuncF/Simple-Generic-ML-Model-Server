import os
from stat import S_ISREG
from task_scheduler import scheduled
import requests
import logging.config
from copy import deepcopy
from flask_api import status
from load_config import get_config

cfg = get_config()
conf = cfg['logging']
logging.config.dictConfig(conf)
log = logging.getLogger(__name__)


class FileWatcher:
    def __init__(self, pmmls_path,
                 extension='.pmml',
                 load_url='http://localhost:9001/load',
                 delete_url='http://localhost:9001/unload',
                 health_url='http://localhost:9001/health',
                 poll_delay_change=2,
                 poll_delay_app_service=2):
        self.pmml_path = pmmls_path
        self.extension = extension
        self.load_url = load_url
        self.delete_url = delete_url
        self.health_url = health_url
        self.files_metadata = {}
        self.poll_delay_change = poll_delay_change
        self.poll_delay_app_service = poll_delay_app_service

    def notify_host_on_change(self, url, file_path):
        try:
            resp = requests.post(url=url, data=file_path)
            return True if f"{resp.status_code}" == f"{status.HTTP_200_OK}" else False
        except Exception as e:
            log.debug(e)
            return False

    def watch(self):
        try:
            while True:
                is_app_running = self.poll_app_service()
                if not is_app_running:
                    if self.files_metadata:
                        self.files_metadata.clear()
                    continue
                self.poll_load()
                self.poll_delete()
        except KeyboardInterrupt:
            log.debug('Polling interrupted by user.')

    @scheduled("poll_delay_change")
    def poll_load(self,):
        for f in os.listdir(self.pmml_path):
            full_path = os.path.join(self.pmml_path, f)
            path_stat = os.stat(full_path)
            _, file_ext = os.path.splitext(f)
            if not S_ISREG(path_stat.st_mode) or str(file_ext) != self.extension:
                continue
            modif_time = path_stat.st_mtime
            current_modif_time = self.files_metadata.get(f)
            if current_modif_time != modif_time:
                is_host_notif_ok = self.notify_host_on_change(
                    self.load_url, full_path)
                if is_host_notif_ok:
                    self.files_metadata.update({f: modif_time})

    @scheduled("poll_delay_change")
    def poll_delete(self,):
        files = os.listdir(self.pmml_path)
        repl_metadata = deepcopy(self.files_metadata)
        for f in repl_metadata.keys():
            if f not in files:
                is_host_notif_ok = self.notify_host_on_change(
                    self.delete_url, f)
                if is_host_notif_ok:
                    self.files_metadata.pop(f)

    @scheduled("poll_delay_app_service")
    def poll_app_service(self,):
        is_app_service_running = self.notify_host_on_change(
            self.health_url, '')
        return is_app_service_running


if __name__ == "__main__":
    cfg = get_config()
    pmml_file_listener = FileWatcher(cfg['watcher']['models_path'])
    log.info(f"Polling started on {cfg['watcher']['models_path']}")
    pmml_file_listener.watch()
