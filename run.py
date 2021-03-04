""" TASKS
run.py should handle configuring of files and calling for asset update
run.py should provide base level UI and options which then disperse requests to sub programs
run.py should be starter and closer and provide the ip address from a seperate program
args to pass: version (if blank configure version on server basis)
"""

from bs4 import BeautifulSoup
import config
import datetime
import os
import platform
import PySimpleGUI as sg
import requests
import shutil
import socket
import server
import wget


# variables
restart_window_on_close = True
restart_edit_window_on_close = False
selected_element = "NONE"
selected_value = "NONE"
version = "1_16_5"

allotcated_RAM_GB = 2
BATCH_FILE_NAME = "auto_start.bat"
if str(platform.system()).lower() == "linux":
    BATCH_FILE_NAME = "auto_start.sh"


# context manager
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
    return requests.get("https://api.ipify.org").text


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())


# primary functions create, edit, host
def create_server(name):
    new_java_server = server.JavaServer(name, version)
    server_jar_name = "minecraft_server_" + version + ".jar"
    batch_command = "java -Xmx" + str(1024*int(allotcated_RAM_GB)) + "M -Xms" + str(1024*int(allotcated_RAM_GB)) + "M -jar " + server_jar_name
    if not new_java_server.does_exist():
        new_java_server.create_self()
        shutil.copy2("Assets/" + server_jar_name, "Servers/" + new_java_server.get_name() + "/" + server_jar_name)
        with cd("Servers/" + new_java_server.get_name()):
            with open(BATCH_FILE_NAME, "w") as file:
                file.write(batch_command)
                new_java_server.save()
                file.close()

            # preform first time host to get server initialized
            os.system(batch_command)

            # accept the EULA
            eula_text = []
            with open("eula.txt", "r") as reader:
                eula_text = reader.readlines()
                eula_text[2] = "eula=true"
                reader.close()
            with open("eula.txt", "w") as writer:
                writer.writelines(eula_text)
                writer.close()


def edit_server(name):
    global restart_edit_window_on_close
    global selected_element
    global selected_value
    global allotcated_RAM_GB

    java_server = server.JavaServer(name, version)
    if java_server.does_exist():
        # load server propertys in the future this is how version control will be implemented
        java_server.load()

        # define editing window
        attributes = []
        with open(config.SERVER_SAVE_LOCATION + java_server.get_name() + "/server.properties", "r") as reader:
            attributes = reader.readlines()
            attributes.pop(0)
            attributes.pop(0)
            reader.close()
        print(attributes)

        batch_command_lines = []
        with open(config.SERVER_SAVE_LOCATION + java_server.get_name() + "/" + BATCH_FILE_NAME, "r") as reader:
            batch_command_lines = reader.readlines()
            reader.close()
        batch_command_lines = batch_command_lines[0]
        batch_command_lines = batch_command_lines.split("Xmx")[1]
        batch_command_lines = batch_command_lines.split("M")[0]
        allotcated_RAM_GB = str(int(batch_command_lines)/1024)

        edit_layout = [
                    [sg.Text("Select element to edit"), sg.Listbox(values=attributes, size=(40, 20)), sg.Button("Select")],
                    [sg.Text("Element: " + str(selected_element) + " = " + str(selected_value)), sg.Text("New Value"), sg.InputText(""), sg.Button("Update")],
                    [sg.Text(java_server.get_name() + " RAM Allocation: " + str(allotcated_RAM_GB) + "GB"), sg.InputText(), sg.Button("Update RAM")],
                    [sg.Button("Exit Editor")]
        ]
        edit_window = sg.Window("Server Editor", edit_layout, size=(800, 600))
        while True:
            event, values = edit_window.read()
            if event == sg.WIN_CLOSED or event == "Exit Editor":
                edit_window.close()
                restart_edit_window_on_close = False
                break

            if event == "Select":
                selected_element_value = str(values[0][0]).split("=")
                selected_element = selected_element_value[0]
                selected_value = selected_element_value[1]
                print(selected_element)
                print(selected_value)

                # restart the window
                restart_edit_window_on_close = True
                edit_window.close()
                break

            if event == "Update":
                print(values[1])
                attributes[attributes.index(str(selected_element + "=" + selected_value))] = str(selected_element + "=" + values[1][0].strip() + "\n")

                with open(config.SERVER_SAVE_LOCATION + java_server.get_name() + "/server.properties", "w") as writer:
                    attributes.insert(0, "#" + datetime.datetime.now().strftime("%b-%d-%I%M%p-%G"))
                    attributes.insert(0, "#Minecraft server properties")
                    writer.writelines(attributes)
                    writer.close()

                # purge old selection to avoid confusion
                selected_element = "update"
                selected_value = "update"

                # refresh the window to see the updated value in the attribute list
                restart_edit_window_on_close = True
                edit_window.close()
                break

            if event == "Update RAM":
                print("New RAM: " + allotcated_RAM_GB)
                allotcated_RAM_GB = values[2].strip()

                # refresh window
                restart_edit_window_on_close = True
                edit_window.close()
                break


def host_server(name):
    java_server = server.JavaServer(name, version)
    if java_server.does_exist():
        terminal_command = ""
        with cd(config.SERVER_SAVE_LOCATION + java_server.get_name() + "/"):
            with open(BATCH_FILE_NAME, "r") as reader:
                terminal_command = reader.readlines()[0]
                reader.close()
            host_layout = [
                        [sg.Text("Hosting Server NOTE: Screen Will Not Update")],
                        [sg.Text("Internal IP: " + str(get_local_ip()))],
                        [sg.Text("External IP: " + str(get_external_ip()))]
            ]
            host_window = sg.Window("Host Window", host_layout)
            while True:
                event, values = host_window.read(timeout=1)
                os.system(terminal_command)
                host_window.close()
                break
            exit()


def get_server_list():
    return [item for item in os.listdir("Servers")]


def run_window():
    global allotcated_RAM_GB
    global restart_window_on_close
    global restart_edit_window_on_close

    layout = [
            [sg.Text("Select Operation", justification="center")],
            [sg.Text("Create Server: "), sg.InputText(), sg.Button("Confirm Creation")],
            [sg.Text("Select Server:"), sg.Listbox(values=get_server_list(), size=(40, 10)), sg.Button("Host"), sg.Button("Edit")],
            [sg.Button("Update Server List")],
            [sg.Text("Current RAM Allocation: " + str(allotcated_RAM_GB) + "GB"), sg.InputText(), sg.Button("Update")],
            [sg.Button("Exit")]
            ]

    sg.theme = ("DarkBrown1")
    window = sg.Window("Minecraft Server Manager", layout, size=(640, 480))
    while True:
        # main menu includes operation options and exit button
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":  # if user closes window or clicks Cancel
            restart_window_on_close = False
            print("Closing")
            break
        if event == "Confirm Creation":
            print("Server name: ", values[0])
            if values[0].strip() != "":
                create_server(str(values[0]).strip())
        if event == "Host":
            print("Server to host: ", values[1][0])
            server_host = server.JavaServer(values[1][0], version)
            if server_host.does_exist():
                window.close()
                host_server(values[1][0])
                exit()
        if event == "Edit":
            stored_RAM = allotcated_RAM_GB
            print("Server to edit: ", values[1][0])
            restart_edit_window_on_close = True
            while restart_edit_window_on_close:
                edit_server(str(values[1][0]).strip())
            allotcated_RAM_GB = stored_RAM
            break
        if event == "Update":
            print("New RAM: ", values[2])
            allotcated_RAM_GB = values[2].strip()
            break
        if event == "Update Server List" or event == "Confirm Creation":
            break
        print("You pressed ", event)
    window.close()


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

    while restart_window_on_close:
        print("Refreshing")
        run_window()
