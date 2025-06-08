import json
import logging
from pathlib import Path
from typing import Any, Dict

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class MemoryStore:
    """Persistent storage for AI Agent HA."""

    def __init__(self, hass: HomeAssistant, file_name: str | None = None) -> None:
        self.hass = hass
        self.file_path = hass.config.path(file_name or "ai_agent_ha_memory.json")
        self.data: Dict[str, Any] = {
            "entities": {},
            "automations": [],
            "dashboards": [],
        }

    async def load(self) -> None:
        """Load memory from disk."""
        def _load(path: str) -> Dict[str, Any] | None:
            if Path(path).is_file():
                with open(path, "r", encoding="utf-8") as file:
                    return json.load(file)
            return None

        try:
            loaded = await self.hass.async_add_executor_job(_load, self.file_path)
            if isinstance(loaded, dict):
                self.data.update(loaded)
            _LOGGER.debug("Memory loaded from %s", self.file_path)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Failed to load memory: %s", err)

    async def save(self) -> None:
        """Save memory to disk."""
        def _save(path: str, data: Dict[str, Any]) -> None:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)

        try:
            await self.hass.async_add_executor_job(_save, self.file_path, self.data)
            _LOGGER.debug("Memory saved to %s", self.file_path)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Failed to save memory: %s", err)
