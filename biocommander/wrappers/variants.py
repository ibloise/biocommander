
from .wrappers import CommandLineSoftware

#TODO: Mejorar la gestion de outputs

class SamtoolsProject(CommandLineSoftware):
    SAM = '.sam'
    BAM = '.bam'
    SORTED = '.sorted'
    BAI = '.bai'
    VCF = '.vcf'

    SUBCMD_SORT = 'sort'
    SUBCMD_VIEW  = 'view'
    SUBCMD_INDEX = 'index'
    SUBCMD_MPILEUP = 'mpileup'

    MPILEUP_REF_FLAG = 'f'

    def add_reference(self, reference):
        self.reference = reference

    def sort(self, input, **kwargs):

        cmd = self._build_command([self.SUBCMD_SORT], kwargs=kwargs, args = input)

        self.execute_command(cmd.cmd_list)
        
    def view(self, input, regions = [], **kwargs):
        
        cmd = self._build_command([self.SUBCMD_VIEW], kwargs=kwargs, args=(input, *regions))
        
        self.execute_command(cmd.cmd_list)

    def index(self, input, **kwargs):

        cmd = self._build_command([self.SUBCMD_INDEX], kwargs=kwargs, args=input)

        self.execute_command(cmd.cmd_list)

    def mpileup(self, input=[], output='', **kwargs):

        if output:
            kwargs['o'] = output

        kwargs[self.MPILEUP_REF_FLAG] = self.reference
        
        cmd = self._build_command([self.SUBCMD_MPILEUP], args = input, kwargs=kwargs)

        self.execute_command(cmd.cmd_list)


    def get_version(self):

        #samtools y bcftools devuelven varias lineas con la versión. Capturamos la primera.

        super().get_version(info_version=False)

        self.version = self.version.splitlines()[0].strip()
        self.logger.info(f'Software version: {self.version}')


class Samtools(SamtoolsProject):

    DEFAULT_COMMAND = 'samtools'

    
    def sam_to_bam(self, input, output):
        self.view(input, S=True, b= True, o = output)
    def bam_to_sam(self, input, output):
        pass

class Bcftools(SamtoolsProject):
    DEFAULT_COMMAND = 'bcftools'

    SUBCMD_CALL = 'call'
    SUBCMD_NORM = 'norm'
    SUBCMD_CONSENSUS = 'consensus'
    SUBCMD_FILTER = 'filter'

    def call(self, input, output, **kwargs):

        kwargs['o'] = output

        cmd = self._build_command([self.SUBCMD_CALL], args=input, kwargs = kwargs)

        self.execute_command(cmd.cmd_list)

    def norm(self, input, output, **kwargs):

        kwargs['o'] = output
        kwargs['f'] = self.reference

        cmd = self._build_command([self.SUBCMD_NORM], args = input, kwargs=kwargs)

        self.execute_command(cmd.cmd_list)

    def filter(self, input, output, **kwargs):

        kwargs['o'] = output

        cmd = self._build_command([self.SUBCMD_FILTER], args = input, kwargs=kwargs)

        self.execute_command(cmd.cmd_list)

    def consensus(self, input, output, **kwargs):

        kwargs['o'] = output
        kwargs['f'] = self.reference

        cmd = self._build_command([self.SUBCMD_CONSENSUS], args = input, kwargs=kwargs)

        self.execute_command(cmd.cmd_list)
