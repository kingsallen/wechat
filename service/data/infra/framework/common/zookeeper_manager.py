# coding:UTF-8

import threading
from kazoo.client import KazooClient

class ZkManager(object):

    zk_clients_cache = {}
    lock = threading.Lock()

    @staticmethod
    def get_zk_client(zookeeper_connect_str):
        with ZkManager.lock:
            zk_client = None
            if zookeeper_connect_str in ZkManager.zk_clients_cache:
                print("get zookeeper client from cache")
                zk_client = ZkManager.zk_clients_cache[zookeeper_connect_str]
            else:
                print("create zookeeper client")
                zk_client = KazooClient(zookeeper_connect_str)
                zk_client.start()
                ZkManager.zk_clients_cache[zookeeper_connect_str] = zk_client
            return zk_client





