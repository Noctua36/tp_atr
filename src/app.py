from threading import Thread
from socket import AF_INET, socket, SOCK_STREAM
from parametros_tanque import parametros
from math import sqrt, pi
import logging
import time
from subprocess import call
# TODO: criar implementação pŕopria do PID
from simple_pid import PID

logging.basicConfig(level=logging.DEBUG)

vazao_in = 0.0
nivel_atual = 8.0
nivel_ref = 10.0  # setpoint
vazao_out = 0.0

pid = PID(1, 0.1, 0.05, setpoint=nivel_ref)
pid.output_limits = (0, 10)
pid.tunings = (1.0, 0.2, 0.4)


class ProcessThread(Thread):
    def __init__(self, cv, raio_inf, raio_sup, altura):
        Thread.__init__(self)
        self.cv = (
            cv
        )  # Coeficiente de descarga do tanque -> relacionado com o tamanho do furo no tanque
        self.raio_inf = raio_inf  # Raio inferior do tanque
        self.raio_sup = raio_sup  # Raio superior do tanque
        self.altura_tanque = altura
        self.alfa = (raio_sup - raio_inf) / altura

    @staticmethod
    def dhdt(self, t, h, u):
        return (
            (-self.cv * sqrt(h) + u) / pi * (self.raio_inf + self.alfa * h) ** 2
            if h > 0
            else 0
        )

    # Runge-Kutta
    @staticmethod
    def rk4(self, f, t0, h0, dt, u):
        f1 = f(self, t0, h0, u)
        f2 = f(self, t0 + dt / 2.0, h0 + dt * f1 / 2.0, u)
        f3 = f(self, t0 + dt / 2.0, h0 + dt * f2 / 2.0, u)
        f4 = f(self, t0 + dt, h0 + dt * f3, u)
        return h0 + dt * (f1 + 2.0 * f2 + 2.0 * f3 + f4) / 6.0

    def run(self):
        global vazao_in, vazao_out, nivel_atual
        lastT = time.time()
        logging.debug("Process Thread iniciada")
        while True:
            now = time.time()
            deltaT = now - lastT
            lastT = now
            nivel_atual = self.rk4(
                self, self.dhdt, lastT, nivel_atual, deltaT, vazao_in
            )
            #logging.debug('nivel_atual = {:.2f}'.format(nivel_atual))
            vazao_out = self.cv * sqrt(nivel_atual)
            time.sleep(0.05)


class SoftPLCThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        logging.debug("Soft PLC Thread iniciada")
        # TODO threading.lock()
        global vazao_in, nivel_atual
        while True:
            vazao_in = pid(nivel_atual)
            #logging.debug('vazao_in = {:.2f}'.format(vazao_in))
            time.sleep(0.05)


class ServerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.host = "0.0.0.0"
        self.port = 30000
        self.addr = (self.host, self.port)
        self.bufSize = 1024
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(self.addr)

    def run(self):
        logging.debug('Server Thread iniciada')
        
        # self.server.bind(self.addr)
        self.server.listen()
        logging.debug('Aguardando conexão do sinóptico')
        conn, cliAddr = self.server.accept()

        # logging.debug('Connectado por' + cliAddr)
        while True:
            # conn.send(b'123')#bytes(nivel_atual, "utf8"))
            conn.send('\nnivel_atual: {:.2f}\nsetpoint: {:.2f}\nvazao_in: {:.2f}\nvazao_out: {:.2f}\n'.format(nivel_atual, nivel_ref, vazao_in, vazao_out).encode())
                # str(nivel_atual).encode())
            time.sleep(1)

            # data = conn.recv(self.bufSize)
            # if not data:
            #     print('sem dados')
            


class Executor:
    def run(self):

        softPLCThread = SoftPLCThread()
        softPLCThread.setDaemon(True)
        softPLCThread.setName("softPLCThread")
        softPLCThread.start()

        processThread = ProcessThread(
            parametros["Cv"],
            parametros["raio_inf"],
            parametros["raio_sup"],
            parametros["altura"],
        )
        processThread.setDaemon(True)
        processThread.setName("processThread")
        processThread.start()

        serverThread = ServerThread()
        serverThread.setDaemon(True)
        serverThread.setName("serverThread")
        serverThread.start()

        time.sleep(2)
        call(["python", "synoptic.py"])

        softPLCThread.join()
        processThread.join()
        serverThread.join()


main = Executor()
main.run()
