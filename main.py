import lib_core.update_core as update_core
import os
import sys

update_core.update_thread("/home/lue/Desktop/new_printer/secrets/config.json")

def restart_script_if_update():
    if "UPDATE" in os.listdir(os.path.join(os.curdir, "tmp", "UPDATE")):
        print("Restarting script...")
        os.remove(os.path.join(os.curdir, "tmp", "UPDATE"))
        os.execv(sys.executable, [sys.executable] + sys.argv)