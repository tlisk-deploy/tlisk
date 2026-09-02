import os
import tempfile
from typing import Any

from loguru import logger
from typing_extensions import override

from libs.config import Config

from .blueprint import Blueprint
from .destinations import Destinations


class Download(Blueprint):
    """
    Blueprint
    """

    name: str = ""
    bp: dict[str, Any] = {}
    valid: bool = False
    tmp_folder: str
    conf: Config

    @override
    def __init__(self, filename: str, bp: dict[str, Any], conf: Config) -> None:
        super().__init__(filename, bp, conf)
        self.name = os.path.splitext(filename)[0]
        self.conf = conf
        self.tmp_folder = ""
        self.bp = bp

        # Check for validity of blueprint if it contains needed components
        self.__check_valid()

        # Misc postprocessing
        self.__postprocessing()

    @override
    def __check_valid(self) -> None:
        """
        Check validity of a blueprint
        """
        if "blueprint" not in self.bp:
            logger.error(f"{self.name}: Blueprint is not wrapped in `blueprint` structure!")
            return

        if "download" not in self.bp["blueprint"]:
            logger.error(f"{self.name}: Deploy is missing from the blueprint!")
            return

        dep = self.bp["blueprint"]["download"]
        if "source" not in dep:
            logger.error(f"{self.name}: `source` configuration is missing from the `deploy` section!")
            return

        if "destinations" not in dep:
            logger.error(f"{self.name}: `destination` configuration is missing from the `deploy` section!")
            return

        self.valid = True

    @override
    def __postprocessing(self):
        """
        Misc. blueprint postprocessing
        """
        if self.valid:
            # Bind authentication to a machine blueprint from master config file if available
            for dest in self.bp["blueprint"]["download"]["destinations"]:
                dest.update(self.conf.get_machine(dest["machine"]))

    @override
    def get_auth(self, auth_name: str, machine: str) -> dict[str, Any]:
        auth_out: dict[str, Any] = {}

        auth = self.conf.get_auth(auth_name)
        auth.update(self.conf.get_machine(machine))

        if "error" in auth and auth["error"]:
            self.valid = False
            return {}

        for key in ["username", "password", "hostname", "port"]:
            if key in auth:
                auth_out.update({key: auth[key]})

        return auth_out

    @override
    def is_active(self) -> bool:
        """
        Clieck if a blueprint is active. It can be disabled with
        'active: false' directive in the blueprint

        Returns:
            bool Is blueprint active
        """
        if not self.valid:
            return False

        if "active" not in self.bp["blueprint"]:
            return True

        return bool(self.bp["blueprint"]["active"])

    @override
    def is_valid(self) -> bool:
        """
        Is blueprint even valid?

        Return
            bool Validity of the blueprint as checked by __check_valid
        """
        return self.valid

    @override
    def set_config(self, conf: Config) -> None:
        """
        Set instance of config file. Usually it's set automatically
        """
        self.conf = conf

    @override
    def set_temp(self, tmp: str) -> None:
        """
        Set temporary folder for some operations
        """
        self.tmp_folder = tmp

    @override
    def get_name(self) -> str:
        """
        Get blueprint (file) name

        Returns
            str Blueprint filename with stripped paths and file extension
        """
        return self.name

    @override
    def get_description(self) -> str:
        """
        Get optional blueprint description

        Returns
            str Blueprint optional description or empty string if the blueprint isn't valid
        """
        if not self.valid or "description" not in self.bp["blueprint"]:
            return ""

        return self.bp["blueprint"]["description"].strip()

    @override
    def get_temp(self) -> str:
        """
        Get temporary folder if one is set or create a new one

        Returns
            str Temporary folder path
        """
        if self.tmp_folder == "":
            self.tmp_folder = tempfile.mkdtemp()

        return self.tmp_folder

    @override
    def get_connection_type(self, machine: str) -> str:
        """
        Get connection type from hosts

        Returns
            str Connection type (FTP,SFTP,WebDAV...)
        """
        conn = self.conf.get_machine(machine)
        if "kind" not in conn:
            return "invalid"

        return conn["kind"].upper()

    @override
    def is_source_local(self) -> bool:
        """
        Checks if source machine is local

        Returns
            bool
        """
        if "machine" not in self.bp["blueprint"]["download"]["source"]:
            return False

        machine: str = self.bp["blueprint"]["download"]["source"]["machine"]
        data: dict[str, Any] = self.conf.get_machine(machine)

        return data["local"]

    @override
    def get_source(self) -> dict[str, str]:
        """
        Get source folder

        Returns
            str Source folder or empty string if the blueprint isn't valid
        """
        if not self.valid:
            return {}

        return self.bp["blueprint"]["download"]["source"]

    @override
    def get_destinatons(self) -> Destinations | list[Any]:
        """
        Get list of destinations

        Returns
            list List of destination or empty list if the blueprint isn't valid
        """
        if not self.valid:
            return []

        return Destinations(self.bp["blueprint"]["download"]["destinations"], self.conf)
