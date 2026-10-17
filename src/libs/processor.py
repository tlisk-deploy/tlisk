import sys
import threading
from argparse import Namespace
from threading import Thread

from colorama import Fore, Style

from libs import agents_registry
from libs.blueprint.blueprint import Blueprint
from libs.blueprint.destinations import Destinations

from .blueprints import Blueprints
from .config import Config
from .transport import Transport


class Processor:
    blueprints: Blueprints
    opts: Namespace
    conf: Config

    def __init__(self, conf: Config, opts: Namespace) -> None:
        self.blueprints = Blueprints(conf, [] if opts.listblueprints else opts.blueprint)
        self.opts = opts
        self.conf = conf

        if opts.listblueprints:
            self.list_blueprints()

        if opts.listcapabilities:
            self.list_capabilities()

    def list_blueprints(self) -> None:
        """
        Pretty display the list of blueprints by name, validity, activity, type,
        and description, and exit.
        """
        # Colors
        bright_green = Style.BRIGHT + Fore.GREEN
        dim_red = Style.DIM + Fore.RED

        bps: dict[str, dict[str, str | bool | Destinations]] = self.blueprints.list_all()
        print(f"{Style.BRIGHT}{Fore.MAGENTA}Available blueprints:")
        for bp in bps:
            is_valid = bright_green + "Valid" if bps[bp]["valid"] else dim_red + "Not valid"
            is_active = bright_green + "Active" if bps[bp]["active"] else dim_red + "Inactive"
            is_valid = is_valid + Style.RESET_ALL
            is_active = is_active + Style.RESET_ALL

            print(f"{Style.BRIGHT}{Fore.YELLOW}{bp}: {is_valid} {Fore.WHITE} || {is_active}")
            if bps[bp]["description"] != "":
                description: str = str(bps[bp]["description"])
                print(f"{Style.DIM}{Fore.WHITE} # {Fore.MAGENTA}{description}")

            print(Style.BRIGHT + Fore.LIGHTBLUE_EX + " Destinations: " + Style.RESET_ALL)
            dests: Destinations = bps[bp]["destinations"]
            for dest in dests:
                is_destination_valid: str = bright_green + "Valid" if dest.is_valid() else dim_red + "Not valid"
                is_destination_valid = is_destination_valid + Style.RESET_ALL
                kind: str = dest.get_kind()
                machine_name: str = str(dest.get_machine())
                print(f"{Style.BRIGHT}{Fore.WHITE}  > {machine_name} ({kind}) | " + is_destination_valid)

            print(Style.RESET_ALL)

        sys.exit(0)

    def list_capabilities(self) -> None:

        print(f"{Style.BRIGHT}{Fore.MAGENTA}Tlisk capabilities:{Style.RESET_ALL}")
        for cap in agents_registry.get_agents().keys():
            print(" - " + Style.BRIGHT + Fore.GREEN + cap + Style.RESET_ALL)

        print(Style.RESET_ALL)
        sys.exit(0)

    def run_blueprint(self, bp: Blueprint) -> None:
        """
        Execute seperate blueprint
        """
        if bp.is_active():
            tx = Transport(bp)
            tx.run()

    def run(self) -> None:
        """
        Run blueprints in threaded environment if executed via CLI
        """
        threads: list[threading.Thread] = []
        # execute threads
        for bp in self.blueprints.get_blueprints():
            t: Thread = threading.Thread(target=self.run_blueprint, args=(bp,))
            threads.append(t)

        # Run threads
        for t in threads:
            t.start()

        # Wait until threads are done
        for t in threads:
            t.join()
