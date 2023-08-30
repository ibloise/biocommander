from .wrappers import CommandLineSoftware
import pandas as pd

class BedTools(CommandLineSoftware):
    #TODO: Quedan formatos que configurar
    DEFAULT_COMMAND = 'bedtools'

    BAM = ".bam"

    IBAM_FLAG = 'ibam'
    INPUT_FLAG = 'i'

    BGA = 'bga'
    BG = 'bg'
    D = "d"

    CHR = 'chr'
    START = 'start'
    END = 'end'
    DEPTH = 'depth'
    NUMBER_EQUAL_2 = "number_bases_depth_equals_depth"
    SIZE = "chr_size"
    FRACTION = "fraction_bases_depth_equals_depth"
    COVERAGE = 'cov'
    POSITION = 'position'

    DEFAULT_COLUMNS = [CHR, DEPTH, NUMBER_EQUAL_2, SIZE, FRACTION]
    BEDGRAPH_COLUMNS = [CHR, START, END, COVERAGE]
    D_FORMAT_COLUMNS = [CHR, POSITION, COVERAGE]

    SUBCMD_GENOMECOV = 'genomecov'
    SUBCMD_MASKFASTA = 'maskfasta'

    genome_cov = ''

    def genomecov(self,  **kwargs):
        #genomecOV sale a las salida estándar
        # Hay que proveer de métodos estandarizados para lectura del STDOUT
        # Para mantener la lógica, estos métodos deben recuperar la salida estándar y mandarla a un archivo en un formato específico.
        # ¿Capacidad de almacenarla a la vez?

        self.logger.info(f"Output will be storaged into the {self.__class__.__name__}.genomecov attribute")
        cmd = self._build_command([self.SUBCMD_GENOMECOV], kwargs=kwargs)

        #Bedtools use all flags with - instead of --
        cmd.long_flag_to_short()

        output = self.execute_command(cmd.cmd_list, capture_output=True)

        if output[self.STDOUT]:
            self.genome_cov = self._deal_genomecov(output[self.STDOUT])
            print(self.genome_cov)
            if self.BGA in kwargs.keys() or self.BG in kwargs.keys():
                self.genome_cov.columns = self.BEDGRAPH_COLUMNS
                self.genome_cov[self.COVERAGE] = pd.to_numeric(self.genome_cov[self.COVERAGE])
            elif self.D in kwargs.keys():
                self.genome_cov.columns = self.D_FORMAT_COLUMNS
                self.genome_cov[self.COVERAGE] = pd.to_numeric(self.genome_cov[self.COVERAGE])
            else:
                self.genome_cov.columns = self.DEFAULT_COLUMNS

        else:
            self.logger.error("Error in process output")

    def filter_coverage_bed(self, output='', threshold = 100):
        #Custom function for create filter BED file to maskfasta

        #Requires genome_cov

        if not self.genome_cov:
            self.logger.error('Requires the execution of genomecov() method')
        self.filter_bed_file = self.genome_cov[self.genome_cov[self.COVERAGE] < threshold]

        self.filter_bed_file.to_csv(output, sep = '\t', header=False, index=False)


    def _deal_genomecov(self, string, col_sep = '\n', row_sep = '\t'):
        #Split the string output of bedtools genomecov and conver into dataframe
        
        rows = string.split(col_sep)
        
        data = [row.split(row_sep) for row in rows]
        
        df = pd.DataFrame(data).dropna()

        return df

    def maskfasta(self, input, bed, output, **kwargs):
        #   Execute maskfasta algorithm

        kwargs['fi'] = input
        kwargs['bed'] = bed
        kwargs['fo'] = output

        cmd = self._build_command([self.SUBCMD_MASKFASTA], kwargs=kwargs)

        cmd.long_flag_to_short()

        self.execute_command(cmd.cmd_list)
                        

