import os

from models import MapConfig


class ConfigSyntaxError(Exception):
    def __init__(
        self,
        line: int,
        file_name: str,
        source: str,
        message: str,
        hint: str | None = None,
    ) -> None:
        self.line: int = line
        self.file_name: str = file_name
        self.source: str = source
        self.message: str = message
        self.hint: str | None = hint

        super().__init__(message)

    def __str__(self) -> str:
        message = str(self.args[0])

        parts = [
            f"{message}",
            f" --> {self.file_name}",
            f"  {self.line - 1}|",
            f" {self.line} | {self.source.rstrip()}",
            f"  {self.line + 1}|",
        ]
        if self.hint:
            parts.append(f"  = hint: {self.hint}")

        return "\n".join(parts)


class ConfigParser:
    _HUB_TYPES: frozenset[str] = frozenset(["start_hub", "end_hub", "hub"])

    @staticmethod
    def _loads_file(path: str) -> list[str]:
        with open(path) as config_file:
            return config_file.readlines()

    def parse(self, path: str = "maps/easy/01_linear_path.txt") -> MapConfig:
        config = MapConfig()

        for lineno, raw in enumerate(self._loads_file(path), start=1):
            line = raw.split("#")[0].strip()
            if not line:
                continue

            keyword, _, rest = line.partition(":")
            rest = rest.strip()
            keyword = keyword.strip()

            try:
                if keyword == "nb_drones":
                    try:
                        config.nb_drones = int(rest)
                    except ValueError:
                        raise ConfigSyntaxError(
                            lineno,
                            os.path.basename(path),
                            raw,
                            "Invalid value for 'nb_drones'",
                            f"expected an integer, got '{rest}'",
                        )

                elif keyword in ConfigParser._HUB_TYPES:
                    ...

                elif keyword == "connection":
                    ...

                else:
                    raise ConfigSyntaxError(
                        lineno,
                        os.path.basename(path),
                        raw,
                        f"Invalid keyword '{keyword}'",
                        (
                            "Expected one of: 'start_hub', 'end_hub', "
                            + "'hub', 'nb_drones', 'connection'"
                        ),
                    )

            except (ValueError, IndexError) as e:
                raise ConfigSyntaxError(
                    lineno, os.path.basename(path), raw, f"{e}"
                )

        return config
