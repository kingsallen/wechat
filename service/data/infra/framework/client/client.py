# coding:UTF-8

import inspect
import traceback
import socket

import tornado

from thrift.transport.TTransport import TTransportException
from kazoo.exceptions import NoNodeError
from kazoo.recipe.watchers import ChildrenWatch

from ...framework.client.connection_pool import ConnectionPool
from ...framework.client.load_balancer.loadbalancer import LoadBalancer
from ...framework.client.load_balancer.loadbalancer import RoundRobinStrategy
from ...framework.common.zookeeper_manager import ZkManager
from ...framework.common import utils


class ServiceClientFactory(object):
    @staticmethod
    def get_service(service_client_cls, conf):
        service_name = utils.get_module_name(service_client_cls).lower()
        return ServiceClient(service_client_cls, service_name, conf).create_proxy()


class ClientRpcException(Exception):
    pass


class ServiceClient(object):
    def __init__(self, service_client_cls, service_name, conf):
        self.service_client_cls = service_client_cls
        self.service_name = service_name
        self.conf = conf
        self._client_pool_map = {}
        self.all_server_nodes = []
        self._watcher_added = False
        self.retry_times = conf.getint("client", "retry_times", default="3")

        self.zk_client = self._connect_to_zookeeper()
        self.service_path = "/service_menu/%s/servers" % self.service_name
        self.fetch_service_server_nodes()
        for server_node in self.all_server_nodes:
            pool = ConnectionPool(server_node, self.service_client_cls, self.service_name, self.conf)
            self._client_pool_map.update({server_node: pool})
        self.load_balancer = LoadBalancer(self.all_server_nodes, RoundRobinStrategy)
        self.register_service_server_nodes_watcher()

    def _connect_to_zookeeper(self):
        zookeeper_connect_str = "{}".format(self.conf.get("zookeeper", "address", required=True))
        zk_client = ZkManager.get_zk_client(zookeeper_connect_str)
        return zk_client

    def _disconnect_from_zookeper(self):
        if self.zk_client:
            while True:
                try:
                    print("trying to close zk client connection")
                    self.zk_client.stop()
                    self.zk_client.close()
                    break
                except:
                    pass
            print("close zk client connection successfully")

    # def close(self):
    #     # clean up resources
    #     self._disconnect_from_zookeper()

    def fetch_service_server_nodes(self):
        def state_listener(state):
            pass

        try:
            service_server_nodes = self.zk_client.get_children(self.service_path)
            for node in service_server_nodes:
                self.all_server_nodes.append(self._to_service_server_nodes(node))
        except NoNodeError as no_node_error:
            print(no_node_error)
        print(self.all_server_nodes)

    def _to_service_server_nodes(self, node_str):
        ip, port = node_str.split(":")
        port = int(port)
        return ip, port, self.service_name

    def register_service_server_nodes_watcher(self):
        try:
            self.zk_client.ensure_path(self.service_path)  # is it necessary?
            ChildrenWatch(self.zk_client, self.service_path, func=self._watch_service_server_nodes)
            self._watcher_added = True
        except NoNodeError as no_node_error:
            print("error: {}, no watcher set up for {}".format(no_node_error, self.service_path))

    def _watch_service_server_nodes(self, server_nodes):
        server_nodes_cached_in_client = set(self.all_server_nodes)
        server_nodes_from_zookeeper = set(self._to_service_server_nodes(node_str) for node_str in server_nodes)

        disappeared_nodes = server_nodes_cached_in_client - server_nodes_from_zookeeper
        if len(disappeared_nodes) > 0:
            self._remove_nodes(disappeared_nodes)

        added_nodes = server_nodes_from_zookeeper - server_nodes_cached_in_client
        if len(added_nodes) > 0:
            self._add_nodes(added_nodes)

    def _remove_nodes(self, nodes):
        print("!" * 100 + "remove nodes" + "!" * 100)
        self._remove_nodes_from_pool(nodes)
        self._remove_nodes_from_load_balancer(nodes)
        self.all_server_nodes = list(set(self.all_server_nodes) - nodes)
        print(self.all_server_nodes)
        print("!" * 100 + "remove nodes" + "!" * 100)

    def _add_nodes(self, nodes):
        print("!" * 100 + "add nodes" + "!" * 100)
        self._add_nodes_to_pool(nodes)
        self._add_nodes_to_load_balancer(nodes)
        self.all_server_nodes = list(set(self.all_server_nodes + list(nodes)))
        print(self.all_server_nodes)
        print("!" * 100 + "add nodes" + "!" * 100)

    def _add_node_to_pool(self, node):
        print("add node to pool {}".format(node))
        if node in self.all_server_nodes:
            return
        pool = ConnectionPool(node, self.service_client_cls, self.service_name, self.conf)
        self._client_pool_map.update({node: pool})
        print(self._client_pool_map)

    def _add_nodes_to_pool(self, nodes):
        for node in nodes:
            self._add_node_to_pool(node)

    def _add_node_to_load_balancer(self, node):
        print("add node to load balancer {}".format(node))
        self.load_balancer.add_backend(node)

    def _add_nodes_to_load_balancer(self, nodes):
        for node in nodes:
            self._add_node_to_load_balancer(node)

    def _remove_node_from_pool(self, node):
        print("remove node from pool {}".format(node))
        if node not in self.all_server_nodes:
            return
        pool = self._client_pool_map.pop(node)
        pool.close()
        print(self._client_pool_map)

    def _remove_nodes_from_pool(self, nodes):
        for node in nodes:
            self._remove_node_from_pool(node)

    def _remove_node_from_load_balancer(self, node):
        print("remove node from load balancer {}".format(node))
        self.load_balancer.remove_backend(node)

    def _remove_nodes_from_load_balancer(self, nodes):
        for node in nodes:
            self._remove_node_from_load_balancer(node)

    def create_proxy(self):
        iface = self.service_client_cls.__bases__[0]
        proxy = iface()
        for m in inspect.getmembers(proxy, predicate=inspect.ismethod):
            setattr(proxy, m[0], self._create_method_proxy(m[0]))
        return proxy

    def _create_method_proxy(self, method_name):
        def _method_proxy(*args):
            return self._method_call(method_name, *args)

        return _method_proxy

    def _get_server_node(self):
        return self.load_balancer.get_backend()

    @tornado.gen.coroutine
    def _method_call(self, method_name, *args):
        retry_times_left = self.retry_times
        while retry_times_left > 0:
            retry_times_left -= 1
            choosen_server_node = self._get_server_node()
            try:
                connection_pool = self._client_pool_map[choosen_server_node]
                connection = yield connection_pool.get_connection()
            except Exception as e:
                if retry_times_left == 0:
                    raise ClientRpcException(e)
                continue
            exc = None
            try:
                result = yield getattr(connection, method_name)(*args)
                yield connection_pool.return_connection(connection)
                return result
            except TTransportException as network_error:
                # network error
                try:
                    traceback.print_exc()
                    connection_pool.release_connection(connection)
                    yield connection_pool.close()
                except Exception as e:
                    exc = e
                else:
                    exc = ClientRpcException("network error")
            except socket.timeout as timeout_error:
                # timeout error
                try:
                    traceback.print_exc()
                except Exception as e:
                    exc = e
                else:
                    exc = ClientRpcException("time out error")
            # TODO:
            # 增加一个对方法异常的捕获, 不然就被下面的通用Exception给拿到了
            # 或者干脆去除通用的Exception?
            except Exception as e:
                # data error
                try:
                    yield connection_pool.return_connection(connection)
                except Exception as inner_e:
                    exc = inner_e
                else:
                    exc = e
            finally:
                if exc and retry_times_left == 0:
                    raise exc
