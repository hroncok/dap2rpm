import os
import tarfile

class DAP(object):
    def __init__(self, path):
        self.path = path
        self.name, self.version = self.get_name_and_version()

    def get_name_and_version(self):
        name_version = os.path.splitext(os.path.basename(self.path))[0]
        return name_version.rsplit('-', 1)

    def extract_info(self):
        pass

    def render(self):
        pass

    def _get_info_from_meta(self, tarhandle):
        info = {}
        meta_path = '{n}-{v}/meta.yaml'.format(n=self.name, v=self.version)

    def _get_dirs_for_rendering(self, tarhandle):
        pass
