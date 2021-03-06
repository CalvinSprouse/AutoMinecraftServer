import shutil
import os

shutil.rmtree("/venv", ignore_errors=True)
os.system("python -m venv venv")
print ("recreated venv")

activate_lines = []
with open("venv/Scripts/activate.bat", "r") as reader:
    activate_lines = reader.readlines()
    reader.close()
    print("activate.bat read")

run_lines = ["cd venv/Scripts"]
run_lines.extend(activate_lines)
run_lines.extend(["cd ..", "cd ..", "python run.py"])
print(run_lines)

with open("run.bat", "w") as writer:
    writer.writelines("%s\n" % line for line in run_lines)
    writer.close()
    print("run.bat created")
    
    
finish_lines = activate_lines
finish_lines.extend(["pip install -r requirements.txt"])
print(finish_lines)
with open("finish_install.bat", "w") as writer:
    writer.writelines("%s\n" % line for line in finish_lines)
    writer.close()
    print("finisher finished")
os.system("finish_install.bat")
os.remove("finish_install.bat")