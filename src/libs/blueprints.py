import os
from glob import glob
from typing import Any, List

import yaml
from loguru import logger

from .blueprint.blueprint import Blueprint
from .blueprint.destinations import Destinations
from .config import Config


class Blueprints:
    bps: list[Blueprint] = []
    conf: Config

    def __init__(self, conf: Config, names: list[str] = []) -> None:
        self.conf = conf
        loc: str = conf.get_blueprints_location()
        if loc != "" and os.path.exists(os.path.expanduser(loc)):
            self.__list(loc, names)
        else:
            logger.error(f"Blueprints path {loc} is unreachable!")

    def __list(self, loc: str, names: list[str] = []) -> None:
        """
        Print the details of a blueprint
        """
        blueprints: List[str] = glob(os.path.join(os.path.expanduser(loc), "*.yaml"))
        data: dict[Any, Any] = {}
        if not names:  # Load all blueprints
            for blueprint in blueprints:
                try:
                    with open(blueprint) as bp:
                        data = yaml.safe_load(bp)
                        self.bps.append(Blueprint(os.path.basename(blueprint), data, self.conf))
                except Exception as e:
                    logger.warning(f"You have an error in blueprint {blueprint}:\n{str(e)}")
        else:  # load single blueprint
            for bp_name in names:
                blueprint = "".join([bp for bp in blueprints if os.path.splitext(os.path.basename(bp))[0] == bp_name])
                if blueprint != "":
                    with open(blueprint) as bp:
                        data = yaml.safe_load(bp)
                        self.bps.append(Blueprint(os.path.basename(blueprint), data, self.conf))
                else:
                    logger.error(f"`{bp_name}` is not in a list of valid blueprints!")

    def list_all(self) -> dict[str, dict[str, str | bool | Destinations]]:
        """
        Returns a brief information about blueprints. Used with `-l` flag

        Returns
            list[dict]
        """
        out: dict[str, dict[str, str | bool | Destinations]] = {}
        for bp in self.bps:
            out[bp.get_name()] = {
                "active": bp.is_active(),
                "valid": bp.is_valid(),
                "sources": bp.get_source(),
                "description": bp.get_description(),
                "destinations": bp.get_destinatons(),
            }

        return out

    def get_blueprints(self) -> list[Blueprint]:
        """
        Return a list of blueprints, regardless of whether they're valid or not.

        Returns
            list List of blueprints
        """
        return self.bps
