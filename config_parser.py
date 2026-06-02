from typing import Any

from models import MapConfig, Hub


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
    HUB_KINDS: dict[str, str] = {
        "start_hub": "start",
        "end_hub": "end",
        "hub": "hub",
    }
    HUB_TYPES: frozenset[str] = frozenset({"start_hub", "end_hub", "hub"})
    VALID_METADATA_KEYS: dict[str, frozenset[str]] = {
        "hub": frozenset(
            {
                "zone",
                "color",
                "max_drones",
            }
        ),
        "connection": frozenset("max_link_capacity"),
    }

    @staticmethod
    def _loads_file(path: str) -> list[str]:
        with open(path) as config_file:
            return config_file.readlines()

    @staticmethod
    def _parse_meta_attrs(keyword: str, meta_attrs: str) -> dict[str, Any]:
        attrs = {}
        for pair in meta_attrs.split():
            key, _, val = pair.partition("=")
            if not key or not val:
                raise ValueError(
                    "Invalid metadata format",
                    "Expected format: 'key=value'",
                )
            keyword_type = "connection" if "hub" not in keyword else "hub"
            validate_metadata_keys = ConfigParser.VALID_METADATA_KEYS[
                keyword_type
            ]
            if key not in validate_metadata_keys:
                raise ValueError(
                    f"Invalid metadata key for {keyword_type}",
                    "Expected one of: "
                    + ", ".join(f"'{key}'" for key in validate_metadata_keys),
                )
            if not val.isalnum():
                raise ValueError(
                    "Invalid value in metadata",
                    f"Expected a valid string or number, got '{val}'",
                )
            attrs[key] = val

        return attrs

    def _split_attrs(self, keyword: str, attrs: str) -> tuple[str, dict]:
        if "[" not in attrs:
            return attrs, {}

        attrs, meta_attrs = attrs.split("[")
        return attrs, self._parse_meta_attrs(keyword, meta_attrs.rstrip("]"))

    def parse(self, path: str = "maps/easy/01_linear_path.txt") -> MapConfig:
        config = MapConfig()

        for lineno, raw in enumerate(self._loads_file(path), start=1):
            line = raw.split("#")[0].strip()
            if not line:
                continue

            keyword, _, attrs = line.partition(":")
            keyword = keyword.strip()
            attrs = attrs.strip()

            try:
                if keyword == "nb_drones":
                    try:
                        config.nb_drones = int(attrs)
                    except ValueError:
                        raise ConfigSyntaxError(
                            lineno,
                            path,
                            raw,
                            "Invalid value for 'nb_drones'",
                            f"Expected an integer, got '{attrs}'",
                        )

                elif keyword in ConfigParser.HUB_TYPES:
                    try:
                        attrs, meta_attrs = self._split_attrs(keyword, attrs)
                    except SyntaxError as e:
                        raise ConfigSyntaxError(
                            lineno,
                            path,
                            raw,
                            e.args[0],
                            e.args[1] if len(e.args) > 1 else None,
                        )
                    parts = attrs.split()
                    hub = Hub(
                        name=parts[0],
                        x=int(parts[1]),
                        y=int(parts[2]),
                        type=ConfigParser.HUB_KINDS[keyword],
                        color=meta_attrs.get("color", "white"),
                        zone=meta_attrs.get("zone", "normal"),
                        max_drones=int(meta_attrs.get("max_drones", 1)),
                    )
                    config.hubs[hub.name] = hub

                elif keyword == "connection":
                    ...

                else:
                    raise ConfigSyntaxError(
                        lineno,
                        path,
                        raw,
                        f"Invalid keyword '{keyword}'",
                        (
                            "Expected one of: 'start_hub', 'end_hub', "
                            + "'hub', 'nb_drones', 'connection'"
                        ),
                    )

            except (ValueError, IndexError) as e:
                raise ConfigSyntaxError(
                    lineno,
                    path,
                    raw,
                    e.args[0],
                    e.args[1] if len(e.args) > 1 else None,
                )

        return config
