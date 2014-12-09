import os
import shutil
import subprocess
import tarfile
import time

import jinja2
import requests
import yaml

from dap2rpm import exceptions

class DAP(object):
    dapi_api_url = 'https://dapi.devassistant.org/api/'

    def __init__(self, path, url=''):
        self.path = path
        self.url = url
        self.name_version, self.name, self.version = self._get_name_and_version()
        self.tarhandle = tarfile.open(self.path, mode='r:*')

    @classmethod
    def get_dap(cls, dapname, version=None, saveto='~/rpmbuild/SOURCES'):
        """Gets DAP from DAPI or local file and saves it to self.saveto

        Args:
            dapname: name of DAP on DAPI or full path to DAP file
            version: version of DAP, used only if DAP is got from DAPI
            saveto: where to save downloaded DAP

        Returns:
            DAP object

        Raises:
            exceptions.DAPGetException if getting the DAP fails
        """
        saveto = os.path.abspath(os.path.expanduser(saveto))

        if dapname.endswith('.dap'):
            return cls._get_dap_local(dapname, saveto)
        else:
            return cls._get_dap_from_dapi(dapname, version, saveto)

    @classmethod
    def _get_dap_from_dapi(cls, dapname, version, saveto):
        """Gets DAP from DAPI and saves it to self.saveto.

        Args:
            dapname: name of DAP on DAPI
            version: version of DAP, used only if DAP is got from DAPI
            saveto: where to save downloaded DAP

        Returns:
            DAP object

        Raises:
            exceptions.DAPGetException if getting the DAP fails
        """
        if version:
            dap_url = '/'.join([cls.dapi_api_url, 'daps', '{0}-{1}'.format(dapname, version)])
        else:
            metadap_url = '/'.join([cls.dapi_api_url, 'metadaps', dapname])
            try:
                dap_url = yaml.load(requests.get(metadap_url).text)['latest']
            except KeyError:
                raise exceptions.\
                    DAPGetException('DAP "{0}" not found on DAPI'.format(dapname))
        try:
            download_url = yaml.load(requests.get(dap_url).text)['download']
        except KeyError:
            raise exceptions.DAPGetException('Can\'t get DAP "{0}", in version "{1}"'.
                format(dapname, version))
        resname = os.path.join(saveto, download_url.split('/')[-1])
        download = requests.get(download_url, stream=True)
        with open(resname, 'wb') as f:
            for chunk in download.iter_content(chunk_size=2048):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return cls(resname, url=download_url)

    @classmethod
    def _get_dap_local(cls, dapname, saveto):
        """Copies dap from a local filesystem to self.saveto.
        Ignores self.version.

        Args:
            dapname: full path to DAP file
            saveto: where to save downloaded DAP

        Returns:
            DAP object

        Raises:
            exceptions.DAPGetException if getting the DAP fails
        """
        resname = os.path.join(saveto, os.path.basename(dapname))
        try:
            shutil.copy2(dapname, resname)
        except IOError as e:
            raise exceptions.DAPGetException('Can\'t get local DAP: {0}'.format(e))
        return cls(resname)

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
        ce = '* {date} {packager} - {version}-1\nInitial package'.format(
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
        info['source_url'] = self._get_macroized_source_url()
        info['requires'] = []
        for r in meta_parsed.get('dependencies', []):
            if not r.startswith('dap-'):
                r = 'dap-' + r
            info['requires'].append(r)
        info['requires'] = list(sorted(info['requires']))
        info['description'] = meta_parsed.get('description', '')
        return info

    def _get_macroized_source_url(self):
        if self.url:  # DAP from DAPI
            parts = self.url.split('/')
            parts[-1] = parts[-1].replace(self.name, '%{shortname}').\
                replace(self.version, '%{version}')
            return '/'.join(parts)
        else:  # DAP from local file
            return '%{name}-%{version}.dap'

    def _get_dirs_for_rendering(self):
        files = self.tarhandle.getnames()
        doc = None
        icons = None
        yaml_dirs = set()
        for f in files:
            if f.startswith(self._nv_opj('doc')):
                doc = self._opj('doc')
            elif f.startswith(self._nv_opj('snippets')):
                yaml_dirs.add(self._opj('snippets'))

            types = ['crt', 'twk', 'prep', 'extra']
            for t in types:
                for d in ['assistants', 'icons']:
                    if f.startswith(self._nv_opj(d, t)):
                        yaml_dirs.add(self._opj(d, t))
            for t in types + ['snippets']:
                if f.startswith(self._nv_opj('files', t)):
                    yaml_dirs.add(self._opj('files', t))

        return {'doc': doc, 'icons': icons, 'yaml_dirs': list(sorted(yaml_dirs))}

    def _nv_opj(self, *paths):
        return os.path.join(self.name_version, *paths)

    def _opj(self, *paths):
        return os.path.join(*paths)
