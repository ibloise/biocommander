from .logger import set_logger

class CliCommand():
    """
    Represents a command line command that can be executed using subprocess.

    Args:
        cmd (str): The main command to be executed.
        subcmds (list, optional): A list of subcommands to be included in the command.
        kwargs (dict, optional): A dictionary containing keyword arguments and their values.
        args (tuple, optional): A tuple of arguments to be included in the command.
        verbosity (int, optional): The verbosity level for logging. Defaults to 20.

    Raises:
        ValueError: If the provided subcommands, keyword arguments, or arguments are not in the correct format.

    Note:
        The CliCommand class provides a convenient way to construct a command line command with subcommands,
        keyword arguments, and arguments. It automatically formats the command into a string or list representation
        that can be executed using subprocess.
    """


    KEY_END = 'end'
    KEY_START = 'start'
    KEY_CMD = 'cmd'
    KEY_SUBCMD = 'subcmds'
    KEY_OPTIONS = 'options'
    KEY_ARGS = 'args'

    KEY_VALUE = 'value'
    KEY_FLAG = 'flag'

    LONG_FLAG_DEFAULT = '--'
    SHORT_FLAG_DEFAULT = '-'


    def __init__(self, cmd, subcmds = None, kwargs =None , args = None, verbosity = 20):
        """
        Initialize the CliCommand object.

        Args:
            cmd (str): The main command to be executed.
            subcmds (list, optional): A list of subcommands to be included in the command.
            kwargs (dict, optional): A dictionary containing keyword arguments and their values.
            args (tuple, optional): A tuple of arguments to be included in the command.
            verbosity (int, optional): The verbosity level for logging. Defaults to 20.

        """

        self.logger = set_logger(self.__class__.__name__, verbosity)
        self.cmd = cmd

        self.subcmds = subcmds

        self.raw_kwargs = kwargs

        if self.raw_kwargs:
            self.kwargs = self._extend_kwargs(self.raw_kwargs)
        else:
            self.kwargs = kwargs
  
        self.raw_args = self._format_arg_tuple(args)

        if self.raw_args:
            self.args = self._build_arg_dict(self.raw_args)
        else:
            self.args = {}

        self.build_cmd()

        self.logger.debug(f'Create command: {self.cmd_str}')

    def add_subcmd(self, subcmds, position=''):
        """
        Adds subcommands to the command at the specified position.

        Args:
        subcmds (list or str): The subcommands to be added. Can be provided as a single subcommand (str) or a list of subcommands (list).
        position (str, optional): The position to add the subcommands. Valid values are 'end' and 'start'. Defaults to 'end'.

        Note:
        If 'position' is not provided or an empty string, the subcommands will be added at the end of the subcommands list.
        If 'position' is set to 'end', the new subcommands will be appended to the existing subcommands list.
        If 'position' is set to 'start', the new subcommands will be inserted at the beginning of the existing subcommands list.

        Raises:
        ValueError: If 'position' is provided but not valid (not 'end' or 'start').

        Example:
        cmd = CliCommand('mycommand')
        cmd.add_subcmd('subcommand1')
        cmd.add_subcmd(['subcommand2', 'subcommand3'], position='start')
        # Resulting subcommands list: ['subcommand2', 'subcommand3', 'subcommand1']
        """

        admit_values = [self.KEY_END, self.KEY_START]

        if not position:
            position = self.KEY_END
        
        if position not in admit_values:
            raise ValueError(f"Invalid 'position' value. Valid values are {', '.join(admit_values)}")

        if not isinstance(subcmds, list):
            subcmds = [subcmds]

        if position == self.KEY_END:
            self.subcmds.extend(subcmds)
        elif position == self.KEY_START:
            subcmds.extend(self.subcmds)
            self.subcmds = subcmds

    def __repr__(self):

        self.cmd_dict = {
            self.KEY_CMD : self.cmd,
            self.KEY_SUBCMD : self.subcmds,
            self.KEY_OPTIONS : self.kwargs,
            self.KEY_ARGS : self.args
        }

        returned = ','.join([f'{key}={value}' for key, value in self.cmd_dict.items()])
        return f'CliCommand({returned})'


    def _format_arg_tuple(self, args):
        """
        Formats the arguments provided as a tuple or in other compatible formats.

        Args:
            args (tuple, str, int, list): The arguments to be formatted. Can be provided as a tuple, a single string or integer,
                                     or a list of arguments.

        Returns:
            tuple or None: The formatted arguments as a tuple, or None if the input format is not compatible.

        Note:
            This method ensures that the arguments are represented as a tuple. If the 'args' parameter is already a tuple,
            it is kept as is. If 'args' is a string or an integer, it is converted into a single-element tuple. If 'args'
            is a list, it is converted into a tuple.

            If the input format for 'args' is not compatible (e.g., an unsupported data type), the method logs an error
            and returns None.
        """

        if isinstance(args, tuple):
            args = args
        elif isinstance(args, str) or isinstance(args, int):
            args = (args,)
        elif isinstance(args, list):
            args = tuple(args)
        else:
            self.logger.error('The args input format is not compatible')
            args = None

        return args
    
    def _extend_kwargs(self, kwarg):
        """
        Extends the keyword arguments provided as a dictionary.

        Args:
            kwarg (dict): The keyword arguments to be extended. Must be provided as a dictionary of {keyword_arg : value}.

        Returns:
            dict: The extended keyword arguments as a dictionary.

        Note:
            This method extends the keyword arguments by formatting and processing each individual keyword argument.
            The 'kwarg' parameter must be a dictionary containing the keyword argument names as keys and their corresponding values.

            The method uses the '_format_kwarg' method to format each keyword argument separately and then combines them
            into a single dictionary containing all the extended keyword arguments.
        """

        extend_kwargs = {}
        for key, value in kwarg.items():

            extend_kwargs.update(self._format_kwarg(key, value))

        return extend_kwargs
    
    def _format_kwarg(self, key, value,  replace_underscores = True):
        """
    Formats a keyword argument as a dictionary entry to be incorporated into the command.

    Args:
        key (str): The keyword argument name.
        value: The value of the keyword argument.
        replace_underscores (bool, optional): If True, replaces dashes ('-') in the keyword argument name with underscores ('_')
                                             to follow common Python naming conventions. Defaults to True.

    Returns:
        dict: A dictionary entry representing the formatted keyword argument.

    Note:
        This method formats a single keyword argument as a dictionary entry with the following structure:
        {key: {self.KEY_VALUE: value, self.KEY_FLAG : flag}}

        The 'key' parameter represents the keyword argument name, and 'value' represents its value.

        The 'replace_underscores' parameter controls whether dashes ('-') in the keyword argument name are replaced
        with underscores ('_') to align with common Python naming conventions for variables.

        The method determines the flag type (long or short) based on the length of the keyword argument name.
        If the name has a length greater than 1, it uses the 'LONG_FLAG_DEFAULT' attribute as the flag prefix, representing
        a long flag (e.g., '--keyword'). If the name has a length of 1 or less, it uses the 'SHORT_FLAG_DEFAULT' attribute,
        representing a short flag (e.g., '-k').

        The formatted keyword argument is returned as a dictionary entry, ready to be used in constructing the command.
        For example, if the original keyword argument 'hello' is provided with the value 'world', the formatted entry
        will be: {'hello': {self.KEY_VALUE: 'world', self.KEY_FLAG: '--'}}
        indicating that the command should include '--hello world'.
        """
        if len(key) > 1:
            flag = self.LONG_FLAG_DEFAULT
        else:
            flag = self.SHORT_FLAG_DEFAULT
        
        if replace_underscores:
            key = key.replace("_", "-")

        return_dict = {key: {self.KEY_VALUE: value, self.KEY_FLAG : flag}}
        
        return return_dict
    
    def long_flag_to_short(self):
        """
    Converts long flags (--) to short flags (-) in the keyword arguments.

    Note:
        Some software, like bedtools, uses single-dash (-) flags for all arguments, even for those with more than one letter.
        This method changes the long flags (--) in the keyword arguments to short flags (-) to make them compatible with
        such cases.

        The method iterates through the keyword arguments and checks if any of them have the long flag prefix (--)
        as defined by the 'LONG_FLAG_DEFAULT' attribute. If a long flag is found, it is replaced with the short flag prefix (-)
        as defined by the 'SHORT_FLAG_DEFAULT' attribute.

        The purpose of this method is to ensure compatibility with software that does not follow the convention of using
        double-dash (--) for long flags.
    """

        for key in self.kwargs.keys():
            if self.kwargs[key][self.KEY_FLAG] == self.LONG_FLAG_DEFAULT:
                self.mod_kwarg(key, flag=self.SHORT_FLAG_DEFAULT)
    
    def mod_kwarg(self, key, new_key = "" ,flag = "", value = ""):
        """
    Modifies a specific keyword argument in the command.

    Args:
        key (str): The name of the keyword argument to modify.
        new_key (str, optional): If provided, renames the keyword argument to this new name. Defaults to an empty string.
        flag (str, optional): If provided, changes the flag of the keyword argument. Defaults to an empty string.
        value: If provided, changes the value of the keyword argument. Defaults to an empty string.

    Note:
        This method allows you to modify a specific keyword argument in the command by changing its name, flag, or value.
        The 'key' parameter represents the original keyword argument name.

        If 'new_key' is provided, the method renames the keyword argument to the new name. This is useful when you want
        to change the keyword argument name while keeping its value and flag intact.

        If 'flag' is provided, the method changes the flag of the keyword argument to the new flag provided.

        If 'value' is provided, the method changes the value of the keyword argument to the new value provided.

        After modifying the keyword argument, the method rebuilds the command to reflect the changes made.
        """

        if flag:
            self.kwargs[key][self.KEY_FLAG] = flag
        
        if value:
            self.kwargs[key][self.KEY_VALUE] = value

        if new_key:
            self.kwargs[new_key] = self.kwargs[key]
            del self.kwargs[key]
        
        self.build_cmd()

    def _preserve_keys(self, src_dict, new_dict):

        """
    Preserves keys from a source dictionary by updating it with new keys and their values.

        Args:
        src_dict (dict): The source dictionary to be updated with new keys and their values.
        new_dict (dict): The dictionary containing the new keys and their values to be added to the source dictionary.

        Returns:
        dict: The updated source dictionary containing the original keys and the new keys with their values.

        Note:
        This method is used in conjunction with the '_add_kwargs' method when 'replace' is set to False.
        It preserves the original keys in the source dictionary by updating it with new keys and their values from the 'new_dict'.

        The method iterates through the 'new_dict' and checks if each key exists in the 'src_dict'.
        If a key does not exist in 'src_dict', it adds the key-value pair to 'src_dict'.

        The purpose of this method is to ensure that when adding new keyword arguments to the command, the original
        keyword arguments are not overwritten, only the new ones are added.
        """

        #method that work in _add_kwargs with replace = False
        #Update dict only with the new keys

        for key, value in new_dict.items():
            if key not in src_dict:
                src_dict[key] = value
        
        return src_dict

    def _build_arg_dict(self, args):
        """
    Builds a dictionary from a tuple of positional arguments.

    Args:
        args (tuple): The tuple containing the positional arguments.

    Returns:
        dict: A dictionary with the positional arguments as values and their corresponding index + 1 as keys.

    Note:
        This method takes a tuple of positional arguments and creates a dictionary where the index of each argument
        in the tuple is used as the key, and the argument itself becomes the value.

        The method uses a dictionary comprehension to achieve this, iterating through the 'args' tuple and assigning
        the positional arguments to their respective keys in the dictionary.

        The purpose of this method is to provide a way to represent positional arguments with their indices, which is
        useful for constructing the command with the correct order of positional arguments.
        """

        args_dict = {idx + 1 : arg for idx, arg in enumerate(args)}

        return args_dict
    
    def _order_args(self):
        """
        Orders the positional arguments in the command dictionary based on their keys.

        Note:
        This method resets the order of the positional arguments in the 'args' dictionary to ensure they are in the correct
        order for constructing the command.

        The method starts by retrieving the keys of the 'args' dictionary and stores them in a list called 'args_order'.
        The keys represent the indices of the positional arguments.

        The list of keys is then sorted in ascending order using the 'sort' method.

        After sorting, the positional arguments are retrieved from the 'args' dictionary in the newly determined order
        and stored in a list called 'args'.

        Finally, the 'args' dictionary is rebuilt using the '_build_arg_dict' method, which creates a new dictionary
        with the positional arguments in the correct order.

        The purpose of this method is to guarantee that the positional arguments in the command are in the correct order,
        ensuring that the command is constructed with the appropriate sequence of arguments.
        """


        args_order = list(self.args.keys())

        args_order.sort()

        args = [self.args[idx] for idx in args_order]

        self.args = self._build_arg_dict(args)

        self.logger.debug(f'Args reordered: {self.args}')

            
    def add_kwargs(self, new_kwargs, replace = False):
        """
    Adds new keyword arguments to the command.

    Args:
        new_kwargs (dict): A dictionary containing the new keyword arguments to be added to the command.
        replace (bool, optional): If True, replaces the existing keyword arguments with the new ones. If False, only
                                  adds the new keyword arguments, preserving the existing ones. Defaults to False.

    Note:
        This method allows you to add new keyword arguments to the command, either by replacing the existing ones or by
        preserving the original ones and adding only the new ones.

        The 'new_kwargs' parameter is a dictionary that contains the new keyword arguments to be added to the command.
        Each key represents the name of a keyword argument, and the corresponding value represents its value.

        If 'replace' is set to True, the existing keyword arguments are replaced with the new ones provided in 'new_kwargs'.
        If 'replace' is set to False, the method updates the existing keyword arguments by adding the new ones, while
        preserving the original ones.

        The method checks if any of the values in 'new_kwargs' are not already formatted as dictionary entries. If a value
        is not a dictionary entry, it formats it using the '_format_kwarg' method to ensure it is in the correct format.

        After updating the keyword arguments, the method rebuilds the command to reflect the changes made.
        """
        temp_new_kwargs = {}
        for key, value in new_kwargs.items():
            # If the value is not already a dictionary, format it using '_format_kwarg'
            if not isinstance(value, dict):
                temp_new_kwargs.update(self._format_kwarg(key, value))
            else:
                temp_new_kwargs[key] = value

    # Update 'new_kwargs' based on the 'replace' parameter
        self.kwargs = self.kwargs.update(new_kwargs) if replace else self._preserve_keys(self.kwargs, temp_new_kwargs)

        self.build_cmd()


    def add_arg(self, new_arg, position=int):
        
        #Obtenemos las posiciones ya existentes

        order = list(self.args.keys())

        order.sort()
        upd_dict = {}
        
        if position in order:

            updates = [value for value in order if value >= position]
            upd_dict = {old + 1 : value for old, value in self.args.items() if old in updates}

        upd_dict[position] = new_arg
        
        self.args.update(upd_dict)

        self.build_cmd()

    def add_multiple_args(self, args, position=''):

        if not position:
            position = self.KEY_END
        
        args = self._format_arg_tuple(args)

        self._order_args()

        if position == self.KEY_END:
            idx_control = len(self.args)
        elif position == self.KEY_START:
            idx_control = 0
        else:
            self.logger.error(f'Only {self.KEY_END} or {self.KEY_START} admitted as position')

        for idx, arg in enumerate(args):
            idx += idx_control
            self.add_arg(arg, idx)
        
        self.build_cmd()

    def _list_kwargs(self):
        #Method for create the list of kwargs needed to build the cmd list
        kwargs_list = []
        for key, format in self.kwargs.items():
            keyword = f'{format[self.KEY_FLAG]}{key}'
            value = format[self.KEY_VALUE]
            kwargs_list.append(keyword)

            if not isinstance(value, bool) and value:
                kwargs_list.append(value)
        
        return kwargs_list
    
    def _list_args(self):

        self._order_args()
        args_list = []

        order = list(self.args.keys())
        order.sort()
        for pos in order:
            args_list.append(self.args[pos])
        
        return args_list

    
    def build_cmd(self):
        """
        Builds the command string and list based on the provided components.

    Note:
        This method constructs both the final command string and the command list using the provided main command,
        subcommands, keyword arguments, and positional arguments.

        The method starts by creating an initial command list containing the main command.

        If subcommands exist, the method extends the command list by adding the subcommands.

        If keyword arguments (kwargs) are present, the method extends the command list with their corresponding flags and values.

        If positional arguments (args) are provided, the method extends the command list with their values.

        Finally, the method joins all elements of the command list into a single string, 'cmd_str', representing the complete command.

        The 'cmd_list' attribute is also updated with the final list, which can be useful if you need to access the individual
        components separately.

        Note that in many cases, it is more convenient and safer to use the 'cmd_list' attribute directly, especially if you
        need to further manipulate or pass the command components to other functions or processes. The 'cmd_str' is provided for
        convenience when a single string representation of the command is required.

        The purpose of this method is to construct the entire command string and list from its components, allowing for a
        flexible and customizable construction process.
        """
        #Add main cmd

        self.cmd_list = [self.cmd]

        #Add subcommands, if exists
        if self.subcmds:
            self.cmd_list.extend(self.subcmds)

        #Add kwargs
        if self.kwargs:
            self.cmd_list.extend(self._list_kwargs())

        if self.args:
            self.cmd_list.extend(self._list_args())
    
        self.cmd_str = ' '.join(self.cmd_list)


