import os
import wget
import requests
import shutil
import socket
import platform
import subprocess
import traceback
import pyinputplus as pyip
from requests import get
from bs4 import BeautifulSoup


# Option Names
CREATE_OPTION_TAG = "create"
HOST_OPTION_TAG = "host"
LIST_OPTION_TAG = "list servers"
EXIT_OPTION_TAG = "exit"

# Constants
USE_GUI = False
VERSION = "1.16.4"
SERVER_FILE_NAME = "server_" + str(VERSION) + ".jar"
PLATFORM = platform.system()

BATCH_FILE_NAME = "auto_start.bat"
if PLATFORM.lower() == "linux":
    BATCH_FILE_NAME = "auto_start.sh"
elif PLATFORM.lower() == "windows":
    BATCH_FILE_NAME = "auto_start.bat"


# Functions
def get_numbered_list(numbered_list):
    return "\n".join("\t{}: {}".format(*k) for k in enumerate(numbered_list))


def get_ip_from_external():
    return get("https://api.ipify.org").text


def get_ip_from_internal():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def list_servers():
    return [item for item in os.listdir()]


def get_download_link():
    url = "https://www.minecraft.net/en-us/download/server"

    page = requests.get(url)
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")

    for link in soup.find_all("a"):
        if "launcher" in link.get("href"):
            return link.get("href")


def main():
    operation = pyip.inputMenu(
        choices=[CREATE_OPTION_TAG, HOST_OPTION_TAG, LIST_OPTION_TAG, EXIT_OPTION_TAG],
        prompt="Select an operation:\n",
        strip=True,
        numbered=True)
    print("> Selection operation " + str(operation))

    if operation == CREATE_OPTION_TAG:
        create()
    elif operation == HOST_OPTION_TAG:
        host()
    elif operation == LIST_OPTION_TAG:
        with cd("Servers"):
            if len(list_servers()) > 0:
                print("\nCurrent Servers:\n" + get_numbered_list(list_servers()) + "\n")
            else:
                print("\nCurrent Servers: None\n")
        main()
    elif operation == EXIT_OPTION_TAG:
        exit()


def create():
    new_server = ""
    with cd("Servers"):
        # list current servers
        if len(list_servers()) > 0:
            print("\nCurrent Servers:\n" + get_numbered_list(list_servers()))
        else:
            print("\nCurrent Servers: None")

        # create new server
        new_server = ""
        while True:
            new_server = pyip.inputStr(prompt="New Server Name (Cannot Be Duplicate):", strip=True)

            if not os.path.exists(new_server):
                if pyip.inputYesNo(prompt="Create server \"" + new_server + "\"? (y/n):") == "yes":
                    break
            else:
                print("\nServer \"" + new_server + "\" already exists")

        # create dir
        os.mkdir(new_server)
        # exit the servers folder to copy assets to new server folder
    # copy assets to server
    if new_server != "":
        shutil.copy2("Assets/" + str(SERVER_FILE_NAME), "Servers/" + new_server + "/server.jar")
        print("> server assets copied")

    # enter new server
    with cd("Servers/" + new_server):
        # create java starter
        with open(BATCH_FILE_NAME, "w") as file:
            if PLATFORM == "Linux":
                file.write("java -Xmx1024M -Xms1024M -jar server.jar nogui\nPause")
            elif PLATFORM == "Windows":
                file.write("@ECHO OFF\njava -Xmx1024M -Xms1024M -jar server.jar nogui\nPause")
        print("> Created " + BATCH_FILE_NAME + " and running")

        # run python start batch
        if PLATFORM == "Linux":
            subprocess.call(["sh", "./" + BATCH_FILE_NAME])
        elif PLATFORM == "Windows":
            subprocess.call([r"" + BATCH_FILE_NAME])

        # accept EULA
        eulaText = []
        with open("eula.txt", "r") as reader:
            eulaText = reader.readlines()
            eulaText[2] = "eula=true"
            reader.close()
        with open("eula.txt", "w") as writer:
            writer.writelines(eulaText)
            writer.close()

        print("> EULA accepted and server generated. Complete server.properties and run in host mode to launch server")
    main()


def host():
    print(os.getcwd())
    try:
        with cd("Servers"):
            # check if servers exist
            if len(list_servers()) < 1:
                print("> No servers found create server first")
                raise CDExitThrowable

            # select a server
            servers = list_servers()
            server_selection = pyip.inputNum(prompt="\nServer Options:\n" + get_numbered_list(servers) + "\n\tSelect Server to Run:", min=0, max=len(servers)-1)
            print("> Selected: " + str(server_selection) + " " + servers[server_selection])

            # operate in server folder
            with cd(servers[server_selection]):
                # check if dir is empty
                if not os.listdir().count("server.jar") > 0:
                    print("> No server.jar found copy server.jar from Assets or delete")
                    exit()

                # code for running the java based server
                with open(BATCH_FILE_NAME, "w") as file:
                    linux_title = "echo -en \"\\033]0;Connect To: " + str(get_ip_from_external()) + " Or LAN: " + str(get_ip_from_internal()) + "\\a\""
                    windows_title = "@ECHO OFF\nTitle Connect To: " + str(get_ip_from_external()) + " Or LAN: " + str(get_ip_from_internal()) + "\n"
                    if USE_GUI:
                        if PLATFORM == "Linux":
                            file.write(linux_title + "\nip address show\njava -Xmx1024M -Xms1024M -jar server.jar\nPause")
                        elif PLATFORM == "Windows":
                            file.write(windows_title + "\njava -Xmx1024M -Xms1024M -jar server.jar\nPause")
                    else:
                        if PLATFORM == "Linux":
                            file.write(linux_title + "\nip address show\njava -Xmx1024M -Xms1024M -jar server.jar nogui\nPause")
                        elif PLATFORM == "Windows":
                            file.write(windows_title + "\njava -Xmx1024M -Xms1024M -jar server.jar nogui\nPause")
                print("> Created " + BATCH_FILE_NAME + " and running")
                print("> Connect to " + str(get_ip_from_external()))

                # run python start batch
                if PLATFORM == "Linux":
                    subprocess.call(["sh", "./" + BATCH_FILE_NAME])
                elif PLATFORM == "Windows":
                    subprocess.call([r"" + BATCH_FILE_NAME])
    except CDExitThrowable:
        main()


# Class
class cd:
    def __init__(self, new_path, print_statement=True):
        self.new_path = os.path.expanduser(new_path)
        self.print_statement = print_statement

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)
        if self.print_statement:
            print("> Operating in:\t" + str(os.getcwd()))

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)
        if self.print_statement:
            print("> Operating in:\t" + str(os.getcwd()))


class CDExitThrowable(Exception):
    pass


# Main
if __name__ == "__main__":
    # move cwd to python script dir
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print("> Operating in:\t" + os.getcwd())

    # if dirs dont exist make them and download files
    if not os.path.exists("Servers"):
        print("> Creating Servers Dir")
        os.mkdir("Servers")

    if not os.path.exists("Assets"):
        print("> Creating Assets Dir")
        os.mkdir("Assets")

    print("> Checking for Assets/server.jar")
    with cd("Assets"):
        if not os.path.isfile(SERVER_FILE_NAME):
            print("> Downloading " + str(VERSION) + " server file")
            wget.download(str(get_download_link()), SERVER_FILE_NAME)

    # start main loop with error handling
    print("> Init complete running main")
    try:
        main()
    except Exception:
        print(traceback.print_exec())
    finally:
        print("> Closing")
        exit()
