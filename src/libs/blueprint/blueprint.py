from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from libs.config import Config

from .destinations import Destinations


class Blueprint(ABC):
    name: str = ""
    bp: dict[str, Any] = {}
    valid: bool = False
    tmp_folder: str
    conf: Config

    @abstractmethod
    def __init__(self, filename: str, bp: dict[str, Any], conf: Config) -> None:
        self.conf = conf
        self.tmp_folder = ""
        self.bp = bp

    @abstractmethod
    def get_auth(self, auth_name: str, machine: str) -> dict[str, Any]:
        logger.warning("`is_active` should be properly initialized!")

    @abstractmethod
    def is_active(self) -> bool:
        logger.warning("`is_active` should be properly initialized!")

    @abstractmethod
    def is_valid(self) -> bool:
        logger.warning("`authenticate` should be properly initialized!")

    @abstractmethod
    def set_config(self, conf: Config) -> None:
        logger.warning("`authenticate` should be properly initialized!")

    @abstractmethod
    def set_temp(self, tmp: str) -> None:
        logger.warning("`authenticate` should be properly initialized!")

    @abstractmethod
    def get_name(self) -> str:
        logger.warning("`authenticate` should be properly initialized!")

    @abstractmethod
    def get_description(self) -> str:
        logger.warning("`authenticate` should be properly initialized!")

    @abstractmethod
    def get_temp(self) -> str:
        logger.warning("`authenticate` should be properly initialized!")

    @abstractmethod
    def get_connection_type(self, machine: str) -> str:
        logger.warning("`get_connection_type` should be properly initialized!")

    @abstractmethod
    def is_source_local(self) -> bool:
        logger.warning("`is_source_local` should be properly initialized!")

    @abstractmethod
    def get_source(self) -> dict[str, str]:
        logger.warning("`get_source` should be properly initialized!")

    @abstractmethod
    def get_destinatons(self) -> Destinations | list[Any]:
        logger.warning("`get_destinatons` should be properly initialized!")
