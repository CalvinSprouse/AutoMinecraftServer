# minecraft server class for creation, hosting, saving config data
import config
import os


class JavaServer:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def does_exist(self):
        return os.path.isdir(str(config.SERVER_SAVE_LOCATION) + self.name)

    def create_self(self):
        os.mkdir("Servers/" + self.name)

    def save(self):
        with open(str(self.name) + "_save.txt", "w") as file:
            file.write(str(self.name) + "\n" + str(self.version))
            file.close()

    def load(self):
        pass

    def set_version(self, version):
        self.version = version

    def get_name(self):
        return self.name

    def get_version(self):
        return self.version
