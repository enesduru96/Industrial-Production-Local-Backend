from configparser import ConfigParser, MissingSectionHeaderError

configFile = "config.ini"
config = ConfigParser()

try:
    config.read(configFile,encoding="utf-8")
except MissingSectionHeaderError:
    config.read(configFile,encoding="utf-8-sig")


DEVICE_URL = str(config["face_device"]["device_url"])
is_home = int(config["home_database"]["is_home"])