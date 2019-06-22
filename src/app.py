from threading import Thread
# import threading
# import socket
from parametros_tanque import parametros
from math import sqrt as raiz, pi
import logging
import time


logging.basicConfig(level=logging.DEBUG)


global vazao_in, vazao_out, nivel_atual, nivel_ref

vazao_in = 0.0
nivel_atual = 8.0
nivel_ref = 10.0 # setpoint
vazao_out = 0.0

class ProcessThread(Thread):
    
    def __init__(self, cv, raio_inf, raio_sup, altura):
        ''' Constructor. '''
        Thread.__init__(self)
        self.Cv = cv # Coeficiente de descarga do tanque -> relacionado com o tamanho do furo no tanque
        self.raio_inf = raio_inf # Raio inferior do tanque
        self.raio_sup = raio_sup # Raio superior do tanque
        self.altura_tanque = altura
    
    def run(self):
        logging.debug('Process Thread iniciada')
        while True:
            global vazao_in, vazao_out, nivel_atual, nivel_ref
            alfa = (self.raio_sup-self.raio_inf)/self.altura_tanque
            vazao_out = self.Cv * raiz(nivel_atual)
            denom = pi*(self.raio_inf+alfa*nivel_atual)**2
            variacao_nivel = -vazao_out/denom + vazao_in/denom
            nivel_atual += variacao_nivel
            logging.debug('nivel_atual = {} \n'.format(nivel_atual))
            time.sleep(0.050)
            

class SoftPLCThread(Thread):
    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)
        
    def run(self):
        logging.debug('Soft PLC Thread iniciada')
        global vazao_in, vazao_out, nivel_atual, nivel_ref

        while True:
            if vazao_in == 0: 
                vazao_in = vazao_out
            if nivel_atual > nivel_ref:
                vazao_in *= 0.95 # diminui 5% da vazao
            elif nivel_atual < nivel_ref:
                vazao_in *= 1.05 # aumenta 5% da vazao
            time.sleep(0.050)

        

# class Synoptic_process(Thread):
#     """docstring for synoptc_process."""
    
#     # def __init__(self, arg):
#         # self.arg = arg

#     def run(self):
#         exibe_info()
#         teclado()

#     def exibe_info(self):
#         global vazao_in, vazao_out, nivel_atual, nivel_ref
#         print('vazao_in = {} \nnivel_atual = {} \nnivel_ref = {}'.format(vazao_in, nivel_atual, nivel_ref))
#         pass
    
#     def teclado(self):
#         pass


class Executor():

    def run(self):
        processThread = ProcessThread(parametros['Cv'], parametros['raio_inf'], parametros['raio_sup'], parametros['altura'])
        processThread.setDaemon(True)
        processThread.start()
        processThread.join()

        softPLCThread = SoftPLCThread()
        softPLCThread.setDaemon(True)
        softPLCThread.start()
        softPLCThread.join()


main = Executor()
main.run()
