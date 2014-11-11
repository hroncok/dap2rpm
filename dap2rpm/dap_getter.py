import os
import shutil

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
        pass

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
