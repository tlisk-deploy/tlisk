import getpass
import os
import sys
from typing import Any

import yaml
from loguru import logger

main_config_file: str = "tlisk.yaml"
default_folders: list[str] = [
    "/etc/tlisk/",
    "~/.local/share/tlisk/",
    "~/.tlisk/",
    "../config/",
    "./config/",
    "./",
]


class Config:
    conf: dict[str, Any] = {}

    def __init__(self, cfgpath: str = "") -> None:
        """
        Scan for default locations if no path is provided else attempt to load config file directly
        """
        if cfgpath == "":
            self.__scan_default_paths()
        else:
            self.__load_config(cfgpath)

        # Init logging
        self.__init_logging()

    def __init_logging(self) -> None:
        """
        Setup app-wide logging
        """
        if "logging" in self.conf:
            if "file" in self.conf["logging"]:
                if "file_format" in self.conf["logging"]:
                    ff = self.conf["logging"]["file_format"]
                else:
                    ff = "{time} {level} {message}"

                logger.add(self.conf["logging"]["file"], colorize=True, format=ff)

            if "stdout_format" in self.conf["logging"]:
                ff = self.conf["logging"]["stdout_format"]
            else:
                ff = "<green>{time}</green> <level>{message}</level>"

            logger.add(sys.stdout, colorize=True, format=ff)

    def __load_config(self, folder: str) -> None:
        """
        Attempt to blindly but safely load YAML file...
        """
        try:
            with open(os.path.join(folder, main_config_file), "r") as f:
                self.conf = yaml.safe_load(f)

            self.__load_external_group(folder, "authentication")
            self.__load_external_group(folder, "machines")

        except Exception as e:
            logger.error(f"Cannot read YAML file!\n{e}")
            sys.exit(1)

    def __scan_default_paths(self) -> None:
        """
        Scan default paths if the path to file isn't provided
        """
        for folder in default_folders:
            folder = os.path.expanduser(folder)
            cfg_file = os.path.join(folder, main_config_file)
            if os.path.exists(cfg_file):
                print(f"Config found in {cfg_file}. Loading...")
                self.__load_config(os.path.dirname(folder))

                return

        logger.error("Cannot locate tlisk.yaml in default locations! Giving up.")
        sys.exit(1)

    def __get_file_location(self, folder: str, loc: str) -> str:
        fn: str = ""

        if os.path.exists(loc):  # Try opening an absolute path
            fn = loc
        else:
            path = os.path.join(folder, loc)  # Try opening relative location to the config file
            if os.path.exists(path):
                fn = path

        return fn

    def __load_external_group(self, folder: str, group: str) -> None:
        """
        Load possible external group from yaml file and bind it to existing config structure

        Returns None
        """
        grp = self.conf[group]
        if type(grp) is str:
            auth_file = self.__get_file_location(folder, grp)

            if auth_file != "":
                try:
                    with open(auth_file, "r") as f:
                        yml_data = yaml.safe_load(f)
                        self.conf[group] = yml_data[group] if group in yml_data else yml_data
                except (TypeError, AttributeError):
                    logger.error(f"Unable to load file '{grp}'!")
                    sys.exit(1)
            else:
                logger.error(f"Unable to load file '{grp}'!")
                sys.exit(1)

    def get_blueprints_location(self) -> str:
        """
        Get path to blueprints from config file

        Returns
            str Blueprints folder
        """
        bp_folder = self.conf["blueprints"] if "blueprints" in self.conf else ""
        if bp_folder != "":
            bp_folder = os.path.expanduser(bp_folder)

        if not os.path.exists(bp_folder) or bp_folder == "":
            logger.error(f"Blueprint folder '{bp_folder}' doesn't exist!")
            sys.exit(1)

        return bp_folder

    def get_machine(self, machine: str) -> dict[str, Any]:
        """
        Get machine details

        Returns
            dict {local, {host, port, authentication}}
        """

        if "machines" in self.conf and type(self.conf["machines"]) is dict and machine in self.conf["machines"]:
            return self.conf["machines"][machine]

        return {}

    def get_auth(self, machine: str) -> dict[str, Any]:
        """
        Gets authentication for a machine from global config file

        Returns
            dict {local, {host, port, authentication}}
        """
        if machine in self.conf["authentication"]:
            auth = self.conf["authentication"][machine]
            if "password" in auth:
                pwd = auth["password"]
                if pwd.lower().startswith("{{") and pwd.endswith("}}"):  # special items
                    print(f"Gathering password for {machine}")
                    pwd_type = pwd.strip("{}").split(".")
                    if len(pwd_type) >= 2 and pwd_type[0].lower() == "$env":
                        # Password in environment. Password directive in yml is {{$ENV.ENVIRONMENT_VARIABLE}}
                        pwd = os.environ[pwd_type[1]] if pwd_type[1] in os.environ else None
                        auth["password"] = pwd
                    elif pwd_type[0].lower() == "$prompt":
                        # Prompt for password. Password directive is {{$PROMPT}}
                        pwd = getpass.getpass() or None
                        auth["password"] = pwd
            return auth
        elif machine == "local":
            return {"local": True}

        msg = f"Authentication for machine {machine} is not in global config file!"
        logger.warning(msg)
        return {"error": True, "message": msg}
