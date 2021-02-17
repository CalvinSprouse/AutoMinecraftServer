# minecraft server class for creation, hosting, saving config data
import config
import os

class JavaServer:
    def __init__(self, name):
        self.name = name

    def does_exist(self):
        return os.path.isfile(str(config.SERVER_SAVE_LOCATION) + self.name)
