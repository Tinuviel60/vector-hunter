from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ComponentFromData(Protocol):
    @classmethod
    def from_data(
        cls, data: dict[str, Any], game_object: Any, context: dict[str, Any]
    ) -> Any:
        ...


class ComponentRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, type[ComponentFromData]] = {}

    def register(
        self, name: str, component_cls: type[ComponentFromData], *, overwrite: bool = False
    ) -> None:
        if not overwrite and name in self._registry:
            raise ValueError(f"Component deja enregistre : {name}")
        self._registry[name] = component_cls

    def get(self, name: str) -> type[ComponentFromData] | None:
        return self._registry.get(name)
