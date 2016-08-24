__author__ = 'zhaobin022'

from core.main import ClientHandler


def start():
    client_handler = ClientHandler()
    client_handler.handler()
def stop():
    print 'in stop'