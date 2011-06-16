import os
import ConfigParser

CONFIG = {}
CONFIG_FILE = "/etc/olympus-validation/config.ini"


def build_config(config_file):
    ret = {}

    if not os.path.exists(config_file):
        raise Exception("%s does not exists" % (config_file))
    config_parser = ConfigParser.ConfigParser()
    config_parser.read(config_file)

    for section in config_parser.sections():
        if not section in ret:
            ret[section] = {}
        for value in config_parser.options(section):
            val = config_parser.get(section, value)
            val = val.replace("'", '').replace('"', '')
            if val.isdigit():
                val = int(val)
            ret[section][value] = val
    return ret


def get_config(config_value):
    config_splitted = config_value.split("/")
    if config_splitted[0] in CONFIG and \
            config_splitted[1] in CONFIG[config_splitted[0]]:
        return CONFIG[config_splitted[0]][config_splitted[1]]

cfg = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   "..", "etc", "config.ini"))
if os.path.exists(CONFIG_FILE):
    CONFIG = build_config(CONFIG_FILE)
elif os.path.exists(cfg):
    CONFIG = build_config(cfg)

if not CONFIG:
    raise Exception("Cannot read config")
