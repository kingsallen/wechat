# coding:UTF-8

import itertools


class NoBackendException(Exception):
    pass


class RoundRobinStrategy(object):

    def update_backends(self, backends):
        self.backends = backends[:]
        self.cycle_iterator = itertools.cycle(self.backends)

    def get_backend(self):
        if len(self.backends) == 0:
            raise NoBackendException()
        return next(self.cycle_iterator)


class LoadBalancer(object):

    def __init__(self, server_nodes, Strategy):
        self.server_nodes = server_nodes
        self.strategy = Strategy()
        self.strategy.update_backends(self.server_nodes)

    def add_backend(self, backend):
        self.server_nodes = set(list(self.server_nodes) + [backend])
        self.strategy.update_backends(list(self.server_nodes))

    def remove_backend(self, backend):
        self.server_nodes = set(self.server_nodes) - set([backend])
        self.strategy.update_backends(list(self.server_nodes))

    def get_backend(self):
        backend = self.strategy.get_backend()
        print(backend)
        return backend
