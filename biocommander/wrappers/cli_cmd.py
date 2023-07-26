from .logger import set_logger

class CliCommand():

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


    def __init__(self, cmd, subcmds = [], kwargs ={} , args = (), verbosity = 20):

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

        admit_values = [self.KEY_END, self.KEY_START]

        if not position:
            position = self.KEY_END
        
        if position not in admit_values:
            self.logger.error(f'Only {" ".join(admit_values)} admitted')

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

        #kwarg must be a dictionary of {keyword_arg : value}

        extend_kwargs = {}
        for key, value in kwarg.items():

            extend_kwargs.update(self._format_kwarg(key, value))

        return extend_kwargs
    
    def _format_kwarg(self, key, value,  replace_underscores = True):

        if len(key) > 1:
            flag = self.LONG_FLAG_DEFAULT
        else:
            flag = self.SHORT_FLAG_DEFAULT
        
        if replace_underscores:
            key = key.replace("_", "-")

        return_dict = {key: {self.KEY_VALUE: value, self.KEY_FLAG : flag}}
        
        return return_dict
    
    def long_flag_to_short(self):

        for key in self.kwargs.keys():
            if self.kwargs[key][self.KEY_FLAG] == self.LONG_FLAG_DEFAULT:
                self.mod_kwarg(key, flag=self.SHORT_FLAG_DEFAULT)
    
    def mod_kwarg(self, key, new_key = "" ,flag = "", value = ""):

        if flag:
            self.kwargs[key][self.KEY_FLAG] = flag
        
        if value:
            self.kwargs[key][self.KEY_VALUE] = value

        if new_key:
            self.kwargs[new_key] = self.kwargs[key]
            del self.kwargs[key]
        
        self.build_cmd()

    def _preserve_keys(self, src_dict, new_dict):

        #method that work in _add_kwargs with replace = False
        #Update dict only with the new keys

        for key, value in new_dict.items():
            if key not in src_dict:
                src_dict[key] = value
        
        return src_dict

    def _build_arg_dict(self, args):

        args_dict = {idx + 1 : arg for idx, arg in enumerate(args)}

        return args_dict
    
    def _order_args(self):

        #Reset args order

        args_order = list(self.args.keys())

        args_order.sort()

        args = [self.args[idx] for idx in args_order]

        self.args = self._build_arg_dict(args)

        self.logger.debug(f'Args reordered: {self.args}')

            
    def add_kwargs(self, new_kwargs, replace = False):

        for key, value in new_kwargs.items():

            if not isinstance(value, dict):
                new_kwargs.update(self._format_kwarg(key, value))

        if replace:
            self.kwargs.update(new_kwargs)
        else:
            self.kwargs = self._preserve_keys(self.kwargs, new_kwargs)
        
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


