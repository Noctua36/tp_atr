from threading import Thread
import socket
from parametros_tanque import parametros
from math import sqrt as raiz, pi
global vazao_in, vazao_out, nivel_atual, nivel_ref

vazao_in = 0.0
nivel_atual = 8.0
nivel_ref = 10.0 # setpoint
vazao_out = 0.0

class Process_tread(Thread):
    """docstring for process_tread."""

    def __init__(self):
        self.Cv = parametros['Cv'] # Coeficiente de descarga do tanque -> relacionado com o tamanho do furo no tanque
        self.raio_inf = parametros['raio_inf'] # Raio inferior do tanque
        self.raio_sup = parametros['raio_sup'] # Raio superior do tanque
        self.altura_tanque = parametros['altura']

    def run(self):
        simula_nivel()

    def simula_nivel(self):
        global vazao_in, vazao_out, nivel_atual, nivel_ref
        alfa = (self.raio_sup-self.raio_inf)/self.altura_tanque
        vazao_out = self.Cv * raiz(nivel_atual)
        denom = pi*(self.raio_inf+alfa*nivel_atual)**2
        variacao_nivel = -vazao_out/denom + vazao_in/denom
        nivel_atual += variacao_nivel


class SoftPLC_thread(Thread):
    """docstring for process_tread."""

    # def __init__(self, arg):
        # self.arg = arg

    def run(self):
        controla_nivel()

    def controla_nivel(self):
        global vazao_in, vazao_out, nivel_atual, nivel_ref
        if vazao_in == 0: vazao_in = vazao_out
        if nivel_atual > nivel_ref:
            vazao_in *= 0.95 # diminui 5% da vazao
        elif nivel_atual < nivel_ref:
            vazao_in *= 1.05 # aumenta 5% da vazao


class Synoptic_process(Thread):
    """docstring for synoptc_process."""
    
    # def __init__(self, arg):
        # self.arg = arg

    def run(self):
        exibe_info()
        teclado()

    def exibe_info(self):
        global vazao_in, vazao_out, nivel_atual, nivel_ref
        print('vazao_in = {} \nnivel_atual = {} \nnivel_ref = {}'.format(vazao_in, nivel_atual, nivel_ref))
        pass
    
    def teclado(self):
        pass


class Mainloop():

    # def run(self): # descomentar essa função e comentar a função abaixo para fazer testes individuais
        # simulacao = Process_tread()
        # simulacao.simula_nivel()
        # controle = SoftPLC_thread()
        # controle.controla_nivel()
        # sinotico = Synoptic_process()
        # sinotico.exibe_info()

    def run(self):
        threads = {
            0: Process_tread,
            1: SoftPLC_thread,
            2: Synoptic_process
        }
        threads_list = list()

        simulacao = threads[0]()
        simulacao.daemon = True
        simulacao.start()
        threads_list.append(simulacao)

        controle = threads[1]()
        controle.daemon = True
        controle.start()
        threads_list.append(controle)

        sinotico = threads[2]()
        sinotico.daemon = True
        sinotico.start()
        threads_list.append(sinotico)


main = Mainloop()
main.run()