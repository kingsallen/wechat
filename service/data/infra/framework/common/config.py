# -*- coding: utf-8 -*-

import os

from configparser import (ConfigParser,
                          NoSectionError,
                          NoOptionError)

class Config(object):

    def __init__(self, file_name=None):
        self.cf = ConfigParser()
        if file_name:
            self._ensure_file_exists(file_name)
            self.cf.read(file_name)

    def _ensure_file_exists(self, file_name):
        file_path = os.path.realpath(file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError("{} not found, path: {}".format(file_name, file_path))

    def set(self, section, option, value):
        if not self.cf.has_section(section):
            self.cf.add_section(section)
        self.cf.set(section, option, value)

    def get(self, section, option, default="", required=False):
        try:
            value = self.cf.get(section, option)
        except (NoSectionError, NoOptionError) as e:
            if required:
                raise e
            value = default
        assert isinstance(value, str)
        return value

    def _get(self, section, option, convert, default, required=False):
        return convert(self.get(section, option, default, required))

    def getint(self, section, option, default="0", required=False):
        return self._get(section, option, int, default, required)

    def getfloat(self, section, option, default="0.0", required=False):
        return self._get(section, option, float, default, required)

    _boolean_mappings = { "True": True, "False": False,
                          "true": True, "false": False }

    def getboolean(self, section, option, default="False", required=False):
        v = self.get(section, option, default, required)
        if v.lower() not in self._boolean_mappings:
            raise ValueError('Not a boolean: %s' % v)
        return self._boolean_mappings[v.lower()]

if __name__ == "__main__":
    conf = Config("./local.conf")
    print(conf.get("zookeeper", "address"))
    print(conf.getboolean("zookeeper", "se_redis", "False"))
    print(conf.getint("zookeeper", "alskdj"))
    conf.set("server", "port", "8888")
    print(conf.getint("server", "port"))
