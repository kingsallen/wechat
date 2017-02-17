# coding=utf-8

from ..thrift_gen.gen.employee.service.EmployeeService import Client as EmployeeServiceClient

from ..framework.client.client import ServiceClientFactory
from ..framework.common.config import Config

import tornado.gen as gen
from tornado import ioloop


@gen.coroutine
def testClient():
    conf = Config("/Users/yiliangt5/moseeker/alphapy/employee_service/service.conf")
    employee_service_cilent = ServiceClientFactory.get_service(EmployeeServiceClient, "employee", conf)

    result = yield employee_service_cilent.getEmployeeRewards(1,3)
    print(result)

def main():
    ioloop.IOLoop.current().run_sync(testClient)


if __name__ == "__main__":
    main()
