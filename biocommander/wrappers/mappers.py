
from .wrappers import CommandLineSoftware
import subprocess
import re

#Vamos a crear el objeto Mapper


class ReadMapper(CommandLineSoftware):
    
    def __init__(self, command='', shell=False, verbosity=20, reference = ''):
        super().__init__(command, shell, verbosity)

        self.reference=reference

    def add_reference(self, reference):
        self.reference = reference


class BwaMapper(ReadMapper):

    SUBCMD_INDEX = 'index'
    SUBCMD_MEM = 'mem'

    SAM_EXT = 'sam'
    DEFAULT_COMMAND = 'bwa'

    def index(self, **kwargs):

        #algo_values = ['is', 'bwtsw']

        cmd = self._build_command([self.SUBCMD_INDEX], kwargs=kwargs, args=self.reference)
        
        self.execute_command(cmd.cmd_list)

    def mem(self, input = [], output='', **kwargs):

        #Add output ¿Specific method?
        
        kwargs['o'] = output
        cmd = self._build_command([self.SUBCMD_MEM], kwargs=kwargs, args=input)

        cmd.add_arg(self.reference, 1)

        self.execute_command(cmd.cmd_list)

    def check_index(self):
        pass

        
    def get_version(self):

        #bwa no tiene flag version, así que vamos a sacarlo del mensaje de error:

        result = subprocess.run(self.command, capture_output=True, text=True)

        version_pattern = r'Version: (\S+)'

        version_match = re.search(version_pattern, result.stderr)

        if version_match:
            self.version = f'{self.command} {version_match.group(1)}'
            self.logger.info(f'Software version: {self.version}')
        else:
            self.logger.warning(self.MSG_VERSION_NOT_FOUND)
            self.version = None

class BowtieMapper(ReadMapper):
    pass

class Minimap2Mapper(ReadMapper):
    pass






