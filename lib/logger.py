import os
from datetime import datetime

class LueLogger:
    def __init__(self, store_in_file: bool = True) -> None:
        self.st_i_f = store_in_file

        if store_in_file:
            log_dir = os.path.join(os.curdir, "tmp", "log")
            os.makedirs(log_dir, exist_ok=True)

        return

    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")
        if self.st_i_f:
            with open(f"{os.curdir}/tmp/log/log-{datetime.now().strftime("%Y-%m-%d")}.log", 'a') as logFile:
                logFile.write(datetime.now().strftime("%H:%M:%S") + " " + msg + "\n")
                logFile.close()

        return