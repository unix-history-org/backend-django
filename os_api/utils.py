import errno
import random
import string
import socket

from django.conf import settings


def get_random_string(length):
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def port_is_free(port): # TODO: REFACTOR THIS
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            return False
        else:
            raise e
    s.close()
    return True


def get_random_port(): # TODO: REWRITE THIS
    rand_port = random.randint(settings.BASE_PORT_SSH_REDIR[0], settings.BASE_PORT_SSH_REDIR[1])
    while not port_is_free(rand_port):
        rand_port = random.randint(settings.BASE_PORT_SSH_REDIR[0], settings.BASE_PORT_SSH_REDIR[1])
    return rand_port
