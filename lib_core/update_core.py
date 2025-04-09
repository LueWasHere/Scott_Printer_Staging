import requests
import json
import os
from datetime import datetime
from lib.logger import LueLogger
import time

def get_latest_code(repo_owner: str, repo_name: str, llogger: LueLogger, branch: str="main", remove_zip: bool=True):
    zip_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{branch}.zip"
    response = requests.get(zip_url)

    if response.status_code == 200:
        tmp_dir = os.path.join(os.curdir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        zip_path = os.path.join(tmp_dir, f"{repo_name}-{branch}.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)

        # Extract the zip file
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        if remove_zip:
            llogger.log("[Updater] Zip removed")
            os.remove(zip_path)

        llogger.log(f"[Updater] Repository {repo_name} downloaded and extracted to {tmp_dir}")
    else:
        llogger.log(f"[Updater] Error downloading repository: {response.status_code} - {response.text}")

def get_latest_commit_hash(repo_owner: str, repo_name: str, llogger: LueLogger, branch: str="main"):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{branch}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["sha"]
    else:
        llogger.log(f"[Updater] Error: {response.status_code}, {response.json().get('message', 'Unknown error')}")
        return None

def check_update(curr_hash: str, repo_owner: str, repo_name: str, llogger: LueLogger, branch: str="main") -> bool:
    """
    returns true if the current code requires an update
    """

    curr_hash_master = get_latest_commit_hash(repo_owner, repo_name, llogger, branch)
    if curr_hash != curr_hash_master:
        return True
    
    return False

def run_update(contentJson: dict, logger: LueLogger) -> None:
    if check_update(contentJson["current_repo_hash"], contentJson["update_repo_author"], contentJson["update_repo_name"], logger, branch=contentJson["update_repo_branch"]):
        logger.log("[Updater] Updating...")
        cur_hash = get_latest_commit_hash(contentJson["update_repo_author"], contentJson["update_repo_name"], logger, branch=contentJson["update_repo_branch"])
        if contentJson["current_repo_hash"] != cur_hash:
            contentJson["current_repo_hash"] = cur_hash

            get_latest_code(contentJson["update_repo_author"], contentJson["update_repo_name"], logger, branch=contentJson["update_repo_branch"])

        logger.log("[Updater] Backing up previous lib...")
        res_int = 0
        res_int += os.system(f"mv {os.curdir}/lib {os.curdir}/lib_BACKUP")
        res_int += os.system(f"mv {os.curdir}/lib_core {os.curdir}/lib_core_BACKUP")
        if res_int != 0:
            logger.log("[Updater] Backup failed, halting")
            return

        res_int = 0
        res_int += os.system(f"mv {os.curdir}/tmp/{contentJson['update_repo_name']}-{contentJson['update_repo_branch']}/lib {os.curdir}/lib")
        res_int += os.system(f"mv {os.curdir}/tmp/{contentJson['update_repo_name']}-{contentJson['update_repo_branch']}/lib_core {os.curdir}/lib_core")
        if res_int != 0:
            logger.log(f"[Updater] Update failed, can't move libs")
            logger.log("Restoring backup...")

            os.system(f"mv {os.curdir}/lib_BACKUP {os.curdir}/lib")
            os.system(f"mv {os.curdir}/lib_core_BACKUP {os.curdir}/lib_core")
            return

        with open(contentJson["secrets_dir"], 'w') as SecretJson:
                json.dump(contentJson, SecretJson)
                SecretJson.close()

        # Place update token so the python script knows to restart
        with open(f"{os.curdir}/tmp/UPDATE", 'a') as f:
            f.close()
    else:
        logger.log("No update necessary")

    return

def update_thread(secrets_dir: str, interval: int=500) -> None:
    logger = LueLogger()
    
    while True:
        try:
            with open(secrets_dir, 'r') as SecretJson:
                contentJson = json.load(SecretJson)
                SecretJson.close()
        except:
            logger.log("[Updater] No secrets? Try creating a \"secrets\" folder in the current directory:\nsecrets/\n|\n\\> config.json\nCreate a config.json in the folder, it should have the following content:\n{\n\t\"update_repo_author\": \"LueWasHere\",\n\t\"update_repo_name\": \"Scott_Printer_Staging\",\n\t\"update_repo_branch\": \"main\",\n\t\"current_repo_hash\": \"\",\n\t\"printer_prid\": \"0\",\n\t\"printer_mnid\": \"0\"\n\"secrets_dir\": \"[The path to the secrets folder]\"\n}\n")
            break

        run_update(contentJson, logger)

        time.sleep(interval)

    return