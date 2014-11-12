import os
import subprocess
import tarfile
import time

import jinja2
import yaml

class DAP(object):
    def __init__(self, path):
        self.path = path
        self.name_version, self.name, self.version = self._get_name_and_version()
        self.tarhandle = tarfile.open(self.path, mode='r:*')

    def extract_info(self):
        info = {'name': self.name, 'version': self.version}
        info.update(self._get_dirs_for_rendering())
        info.update(self._get_info_from_meta())
        info['changelog_entry'] = self._get_changelog_entry()
        return info

    def render(self):
        jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('dap2rpm', '.'),
            trim_blocks=True, lstrip_blocks=True)
        template = jinja_env.get_template('spec.template')
        return template.render(**self.extract_info())

    def _get_name_and_version(self):
        name_version = os.path.splitext(os.path.basename(self.path))[0]
        return [name_version] + name_version.rsplit('-', 1)

    def _get_changelog_entry(self):
        packager = subprocess.check_output(['rpmdev-packager']).decode('utf-8').strip()
        ce = '{date} {packager} - {version}-1\nInitial package'.format(
            date=time.strftime('%a %b %d %Y', time.gmtime()),
            packager=packager,
            version=self.version)
        return ce

    def _get_info_from_meta(self):
        info = {}
        meta_path = self._nv_opj('meta.yaml')
        meta_yaml = self.tarhandle.extractfile(meta_path)
        meta_parsed = yaml.load(meta_yaml)
        info['summary'] = meta_parsed.get('summary', '')
        info['license'] = meta_parsed.get('license', '')
        info['url'] = meta_parsed.get('homepage', '')
        # TODO: source URL
        info['requires'] = []
        for r in meta_parsed.get('dependencies', []):
            if not r.startswith('dap-'):
                r = 'dap-' + r
            info['requires'].append(r)
        info['requires'] = list(sorted(info['requires']))
        info['description'] = meta_parsed.get('description', '')
        return info

    def _get_dirs_for_rendering(self):
        files = self.tarhandle.getnames()
        doc = None
        assistant_dirs = set()
        for f in files:
            if f.startswith(self._nv_opj('doc')):
                doc = self._opj_n('doc')
            for i in ['icons', 'snippets']:
                if f.startswith(self._nv_opj(i)):
                    assistant_dirs.add(self._opj_n(i))
            for i in ['crt', 'twk', 'prep', 'extra']:
                if f.startswith(self._nv_opj('assistants', i)):
                    assistant_dirs.add(self._opj_n('assistants', i))
        return {'doc': doc, 'assistant_dirs': list(sorted(assistant_dirs))}

    def _nv_opj(self, *paths):
        return os.path.join(self.name_version, *paths)

    def _opj_n(self, *paths):
        return os.path.join(*(paths + (self.name,)))
