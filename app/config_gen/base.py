from abc import ABC, abstractmethod
from pathlib import Path


class BaseConfigGenerator(ABC):
    """Базовый класс для генераторов конфигов"""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def generate(self) -> None:
        """Сгенерировать и записать конфиг на диск"""
        ...

    def write(self, content: str) -> None:
        """Записать конфиг на диск"""
        self.config_path.write_text(content, encoding="utf-8")
