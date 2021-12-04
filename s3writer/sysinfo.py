import os
import psutil
from time import time
from threading import Timer, Thread, Lock
from opensearchclient import OpenSearchClient, Index
from collections import Counter

RUN_INTREVAL = 3

class SysInfo(object):
    def __init__(self, opensearch:OpenSearchClient, exchange:str, topic:str, taskid: str):
        self.opensearch = opensearch
        self.index = Index(opensearch, "sysinfo", exchange=exchange, topic=topic, taskid=taskid)
        self.stopped = False
        self.thread = None
        self.mutex = Lock()
        self.netcounters = None

    def thread_function(self):
        self.mutex.acquire()

        if self.stopped:
            self.index.delete()
            print('sysinfo thread stopped')
            return

        try:
            Timer(int(time()/RUN_INTREVAL)*RUN_INTREVAL+RUN_INTREVAL - time(), self.thread_function).start ()
            cpu_usage = psutil.cpu_percent()
            ram_usage = psutil.virtual_memory()[2]
            netcounters = psutil.net_io_counters()._asdict()
            net_usage = Counter(netcounters)
            net_usage.subtract(self.netcounters)
            self.netcounters = netcounters

            data = {
                "CPU": cpu_usage,
                "RAM": ram_usage,
                "NET": dict(net_usage)
            }

            self.index.add_document(data)

        finally:
            self.mutex.release()

    def Start(self):
        self.thread = Thread(target=self.thread_function, args=())
        self.thread.start()

    def Stop(self):
        self.mutex.acquire()
        self.stopped = True
        self.mutex.release()
        if self.thread:
            self.thread.join()
