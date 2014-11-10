import os
import shutil

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
            TODO exception if DAP doesn't exist or the specified version doesn't exist
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
            TODO exception if DAP doesn't exist or the specified version doesn't exist
        """
        pass

    def get_dap_local(self):
        """Copies dap from a local filesystem to self.saveto.
        Ignores self.version.

        Returns:
            full path to saved DAP

        Raises:
            TODO exception if DAP doesn't exist
        """
        resname = os.path.join(self.saveto, os.path.basename(self.dapname))
        shutil.copy2(self.dapname, resname)
        return resname
