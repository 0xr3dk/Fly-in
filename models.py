from dataclasses import dataclass, field


@dataclass
class Hub:
    name: str
    x: int
    y: int
    type: str
    color: str = "white"
    max_drones: int = 1
    zone: str | None = None


@dataclass
class Connection:
    source: str
    target: str
    max_link_capacity: int | None = None


@dataclass
class MapConfig:
    nb_drones: int = 0
    hubs: dict[str, Hub] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
