from __future__ import annotations

import configparser
import json
from typing import Any

from pydantic import BaseModel


class DBBaseModel(BaseModel):  # type: ignore

    async def as_db_item(self, db_model: Any) -> Any:
        raise NotImplementedError()

    def serialize(self) -> bytes:
        ...
        raise NotImplementedError()

    def filter_statement(self) -> str:
        raise NotImplementedError()


class ScreenSection(BaseModel):  # type: ignore
    top: int
    left: int
    width: int
    height: int

    def mss_monitor_dict(self) -> dict[str, int]:
        return {
            "top": self.top,
            "left": self.left,
            "width": self.width,
            "height": self.height,
        }


class Configuration(BaseModel):  # type: ignore

    trail_completed_image_location: ScreenSection
    inventory_image_location: ScreenSection
    use_gpu_processing: bool = False

    def from_config_file(self, filename: str) -> None:
        config = configparser.ConfigParser()
        config.read(filename)

        self._get_screensection_values(config["ScreenSections"])
        self.use_gpu_processing = bool(
            config["ImageProcessing"]["use_gpu_processing"],
        )

    def _get_screensection_values(self, data_dict: configparser.SectionProxy) -> None:
        for key, value in data_dict.items():
            values = json.loads(value)
            setattr(
                self,
                f"{key}_location",
                ScreenSection(
                    top=values["top"],
                    left=values["left"],
                    width=values["width"],
                    height=values["height"],
                ),
            )


if __name__ == "__main__":
    config = Configuration()
    config.from_config_file(
        filename=("C:\\Development\\RS3\\ClueEvaluator\\ClueEvaluatorLib\\data\\config.ini"),
    )
    print(config.trail_completed_image_location)
    print(config.inventory_image_location)
    print(config.use_gpu_processing)
