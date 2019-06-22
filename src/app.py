from threading import Thread
# import threading
# import socket
from parametros_tanque import parametros
from math import sqrt, pi
import logging
import time


logging.basicConfig(level=logging.DEBUG)

vazao_in = 0.0
nivel_atual = 8.0
nivel_ref = 10.0 # setpoint
vazao_out = 0.0

class ProcessThread(Thread):
    
    def __init__(self, cv, raio_inf, raio_sup, altura):
        ''' Constructor. '''
        Thread.__init__(self)
        self.cv = cv # Coeficiente de descarga do tanque -> relacionado com o tamanho do furo no tanque
        self.raio_inf = raio_inf # Raio inferior do tanque
        self.raio_sup = raio_sup # Raio superior do tanque
        self.altura_tanque = altura
        self.alfa = (raio_sup-raio_inf)/altura
    
    @staticmethod
    def dhdt(self, t, h, u):
        return (-self.cv*sqrt(h)+u)/pi*(self.raio_inf+self.alfa*h)**2 if h>0 else 0

    # Runge-Kutta
    @staticmethod
    def rk4(self, f, t0, h0, dt, u):
        f1 = f(self, t0, h0, u)
        f2 = f(self, t0+dt/2.0, h0+dt*f1/2.0, u)
        f3 = f(self, t0+dt/2.0, h0+dt*f2/2.0, u)
        f4 = f(self, t0+dt, h0+dt*f3, u)
        return h0+dt*(f1+2.0*f2+2.0*f3+f4)/6.0

    def run(self):
        global vazao_in, vazao_out, nivel_atual, nivel_ref
        lastT = time.time()
        logging.debug('Process Thread iniciada')
        while True:
            now = time.time()
            deltaT = now - lastT
            lastT = now
            nivel_atual = self.rk4(self, self.dhdt, lastT, nivel_atual, deltaT, vazao_in)
            logging.debug('nivel_atual = {}'.format(nivel_atual))
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
        processThread.setName('processThread')
        processThread.start()
        processThread.join()

        softPLCThread = SoftPLCThread()
        softPLCThread.setDaemon(True)
        processThread.setName('softPLCThread')
        softPLCThread.start()
        softPLCThread.join()


main = Executor()
main.run()
