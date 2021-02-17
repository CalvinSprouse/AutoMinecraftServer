# run the server manager

# TASKS
# run.py should handle configuring of files and calling for asset update
# run.py should provide base level UI and options which then disperse requests to sub programs
# run.py should be starter and closer and provide the ip address from a seperate program
# args to pass: version (if blank configure version on server basis)

import requests
import os
import wget
import config
import server
from bs4 import BeautifulSoup

# variables

# context manager

# file updating device
def download_server_jar(local_location):
    url = "https://www.minecraft.net/en-us/download/server"
    page = requests.get(url)
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")

    for link in soup.find_all("a"):
        if "launcher" in link.get("href"):
            minecraft_server_string = str(link)[str(link).find("minecraft_server"):]
            full_version_string = minecraft_server_string[:minecraft_server_string.find(".jar")].replace(".", "_")
            file_name = local_location + str(full_version_string) + ".jar"

            if not os.path.isfile(file_name):
                wget.download(str(link.get("href")), file_name)
                print("\n")
                return True
            else:
                return False

# retrieve IP
def get_external_ip():
    return get("https://api.ipify.org").text


def get_local_ip():
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

# primary functions create, edit, host
def create_server():
    pass

def edit_server():
    pass

def host_server():
    pass


# main
if __name__ == "__main__":
    # move cwd to python script dir
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print("> Operating in:\t" + os.getcwd())

    # if dirs dont exist make them and download files
    if not os.path.exists(config.SERVER_SAVE_LOCATION):
        print("> Creating Servers Dir")
        os.mkdir(config.SERVER_SAVE_LOCATION)

    if not os.path.exists(config.ASSET_SAVE_LOCATION):
        print("> Creating Assets Dir")
        os.mkdir(config.ASSET_SAVE_LOCATION)

    print("> Checking for Assets/server.jar")
    if download_server_jar(config.ASSET_SAVE_LOCATION):
         print("> Most up to date assets downloaded")
    else:
        print("> Most up to date assets already downloaded")

    # now enter main UI loop and choose function (create server, edit server, host server, exit)
