import os
import shutil

import requests
import yaml

from dap2rpm import exceptions

class DAPGetter(object):
    def __init__(self, dapname, version=None, saveto='~/rpmbuild/SOURCES'):
        self.dapname = dapname
        self.version = version
        self.saveto = os.path.abspath(os.path.expanduser(saveto))
        self.dapi_api_url = 'https://dapi.devassistant.org/api/'

    def get_dap(self):
        """Gets DAP from DAPI or local file and saves it to self.saveto

        Returns:
            full path to saved DAP

        Raises:
            exceptions.DAPGetException if getting the DAP fails
        """
        if self.dapname.endswith('.dap'):
            return self.get_dap_local()
        else:
            return self.get_dap_from_dapi()

    def get_dap_from_dapi(self):
        """Gets DAP from DAPI and saves it to self.saveto.

        Returns:
            full path to saved DAP

        Raises:
            exceptions.DAPGetException if getting the DAP fails
        """
        if self.version:
            dap_url = '/'.join([self.dapi_api_url, 'daps',
                '{0}-{1}'.format(self.dapname, self.version)])
        else:
            metadap_url = '/'.join([self.dapi_api_url, 'metadaps', self.dapname])
            try:
                dap_url = yaml.load(requests.get(metadap_url).text)['latest']
            except KeyError:
                raise exceptions.\
                    DAPGetException('DAP "{0}" not found on DAPI'.format(self.dapname))
        try:
            download_url = yaml.load(requests.get(dap_url).text)['download']
        except KeyError:
            raise exceptions.DAPGetException('Can\'t get DAP "{0}", in version "{1}"'.
                format(self.dapname, self.version))
        resname = os.path.join(self.saveto, download_url.split('/')[-1])
        download = requests.get(download_url, stream=True)
        with open(resname, 'wb') as f:
            for chunk in download.iter_content(chunk_size=2048):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return resname

    def get_dap_local(self):
        """Copies dap from a local filesystem to self.saveto.
        Ignores self.version.

        Returns:
            full path to saved DAP

        Raises:
            exceptions.DAPGetException if getting the DAP fails
        """
        resname = os.path.join(self.saveto, os.path.basename(self.dapname))
        try:
            shutil.copy2(self.dapname, resname)
        except IOError as e:
            raise exceptions.DAPGetException('Can\'t get local DAP: {0}'.format(e))
        return resname
