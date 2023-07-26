
import subprocess
from .logger import set_logger
from .cli_cmd import CliCommand
import os


#TODO:  Gestión de posicionales en la creación del comando
#       Gestión de argumentos duplicados
#       Gestión de software con posibilidad de vectorización?
#       Creación del comando global


class CommandLineSoftware():

    #Messages
    MSG_SHELL_WARNING = 'WARNING: Shell function is enabled'
    MSG_VERSION_NOT_FOUND = 'WARNING: Software version non located'
    MSG_NOT_COMMAND = 'ERROR: Default command abscence and not alternative command availaible'

    DEFAULT_COMMAND = ''

    VERSION_FLAGS = ['--version', '-v' ]

    STDOUT = 'stdout'
    STDERR = 'stederr'
    KWARGS = 'kwargs'
        
    def __init__(self, command ='', shell = False, verbosity = 20):
        
        self.verbosity = verbosity
        self.logger = set_logger(self.__class__.__name__, self.verbosity)

        self._shell = shell


        if command:
            self.command = command
        elif self.DEFAULT_COMMAND:
            self.command = self.DEFAULT_COMMAND
        else:
            self.logger.error(self.MSG_NOT_COMMAND)
            exit()
        
        self.cli_command = ''
        self.get_version()
        self._shell_warning()

    def _shell_warning(self):

        if self._shell:
            self.logger.warning(self.MSG_SHELL_WARNING)

    def _build_command(self, subcommands = [], args = (), kwargs = {}):
        #Subcommand must be in order!!

        cli_command = CliCommand(
            cmd=self.command,
            subcmds=subcommands,
            kwargs=kwargs,
            args=args,
            verbosity=self.verbosity
        )

        return cli_command

    def dynamic_output(self, input, output_extension):
        #Not work. FIx

        input_name = os.path.splitext(os.path.basename(input))

        output = f'{input_name}.{output_extension}'

        return output


    def execute_command(self, cmd, capture_output = False):
        
        if not isinstance(cmd, list):
            self.logger.warning('Executing command string instead of list are more insecure! Please, consider use list')
        self.logger.info(f'Executing: {" ".join(cmd)}')

        result = subprocess.run(cmd, shell=self._shell, capture_output=capture_output)

        if capture_output:
            return self.capture_output(result)
        
    def get_version(self, info_version = True):

        self.version = None
        for version_flag in self.VERSION_FLAGS:
            version = subprocess.run([self.command, version_flag], capture_output=True, text=True)
            if version.stdout:
                self.version = version.stdout.strip()
                if info_version:
                    self.logger.info(f'Software version: {self.version}')
                break

        if not self.version:
            self.logger.warning(self.MSG_VERSION_NOT_FOUND)

    def capture_output(self, output):
        #Capture and standarized the output of subprocess


        output_dict = {
            self.STDOUT : output.stdout.decode('utf-8'),
            self.STDERR : output.stderr.decode('utf-8'),
        }

        return output_dict





