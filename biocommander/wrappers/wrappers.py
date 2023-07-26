
import subprocess
from .logger import set_logger
from .cli_cmd import CliCommand
import os


#TODO:  Gestión de los mensajes. 
#       Gestión de argumentos duplicados
#       Gestión de software con posibilidad de vectorización?


class CommandLineSoftware():
    """
    Provides basic functionality for other classes in BioCommander.
    This class should not be instantiated by itself.

    Attributes:
        MSG_SHELL_WARNING (str): Warning message for enabling shell function.
        MSG_VERSION_NOT_FOUND (str): Warning message for non-located software version.
        MSG_NOT_COMMAND (str): Error message for absence of default command and no alternative command available.

        DEFAULT_COMMAND (str): Default command for the software.

        VERSION_FLAGS (list): List of flags to check the software version.

        STDOUT (str): Constant representing standard output.
        STDERR (str): Constant representing standard error.
        KWARGS (str): Constant representing keyword arguments.

    Args:
        command (str, optional): The command for the software. If not provided, it will be set to the DEFAULT_COMMAND if available.
        shell (bool, optional): If True, enables the shell function for command execution. Defaults to False.
        verbosity (int, optional): The verbosity level for logging. Defaults to 20.

    Note:
        This class should be used as a base class and should not be instantiated directly.
    """

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
        """
        Initialize the CommandLineSoftware object.

        Args:
            command (str, optional): The command for the software. If not provided, it will be set to the DEFAULT_COMMAND if available.
            shell (bool, optional): If True, enables the shell function for command execution. Defaults to False.
            verbosity (int, optional): The verbosity level for logging. Defaults to 20.
        """
        
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

        self.last_outputs = {}
        self.get_version()
        self._shell_warning()

    def _shell_warning(self):

        if self._shell:
            self.logger.warning(self.MSG_SHELL_WARNING)

    def _build_command(self, subcommands = None, args = (), kwargs = {}):
        """
        Builds the command for execution based on the provided subcommands, arguments, and keyword arguments.

        Args:
            subcommands (list, optional): A list of subcommands to include in the command.
            args (tuple, optional): A tuple of arguments to include in the command.
            kwargs (dict, optional): A dictionary of keyword arguments to include in the command.

        Returns:
            CliCommand: An instance of the CliCommand class representing the built command.

        Note:
            The subcommands must be provided in the correct order, as they will be used to construct the command in sequence.
        """
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
        """
        Executes the provided command and returns the result.

        Args:
            cmd (list or str): The command to be executed, provided as a list or a string.
            capture_output (bool, optional): If True, captures the command's output. Defaults to False.

        Returns:
            CompletedProcess or dict: The CompletedProcess object returned by subprocess.run if capture_output is False,
            otherwise, a dictionary containing the captured standard output and standard error as strings.

        Note:
            Executing the command as a list is considered more secure than executing it as a string.
        """
        
        if not isinstance(cmd, list):
            self.logger.warning('Executing command string instead of list are more insecure! Please, consider use list')
        self.logger.info(f'Executing: {" ".join(cmd)}')

        result = subprocess.run(cmd, shell=self._shell, capture_output=capture_output)

        if capture_output:
            return self.capture_output(result)
    
    def launch_command(self, subcommands=None, args = (), kwargs = None, capture_output= False ):
        """
        Constructs and executes the command based on the provided subcommands, arguments, and keyword arguments.

        Args:
            subcommands (list, optional): A list of subcommands to include in the command. Defaults to None.
            args (tuple, optional): A tuple of arguments to include in the command. Defaults to an empty tuple.
            kwargs (dict, optional): A dictionary of keyword arguments to include in the command. Defaults to None.
            capture_output (bool, optional): If True, captures the command's output. Defaults to False.

        Note:
            The 'subcommands' parameter is a list, 'args' is a tuple, and 'kwargs' is a dictionary.
        """

        cmd = self._build_command(subcommands, args, kwargs)
        self.execute_command(cmd.cmd_list, capture_output=capture_output)
        
    def get_version(self, info_version = True):
        """
        Retrieves the software version using the provided VERSION_FLAGS.

        Args:
            info_version (bool, optional): If True, logs the software version if found. Defaults to True.
                Set info_version to False when the subclass needs to perform specific manipulations
                of the version output

        Note:
            If the software version is not found, a warning message is logged.
        """

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

    def trace_output(self, output, method):
        """
        Stores the output filename of a method in the last_outputs dictionary.

        Args:
            output (str): The output to be stored.
            method (str): The name of the method generating the output.
        """

        self.last_outputs[method] = output

    def capture_output(self, output):
        """
        Captures and standardizes the output of a subprocess.

        Args:
            output (CompletedProcess): The CompletedProcess object returned by subprocess.run.

        Returns:
            dict: A dictionary containing the captured standard output and standard error as strings.
        """

        output_dict = {
            self.STDOUT : output.stdout.decode('utf-8'),
            self.STDERR : output.stderr.decode('utf-8'),
        }

        return output_dict





