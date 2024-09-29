from __future__ import annotations

from typing import Optional

from ClueEvaluatorLib.src.models.base import DBBaseModel
from ClueEvaluatorLib.src.models.dbhandler import DataBaseHandler
from ClueEvaluatorLib.src.models.items import Item
from ClueEvaluatorLib.src.models.util import FileReader

from ClueEvaluatorLib.src.models.statistics import InitParams, Statistics, WealthEvaluator  # isort: skip


class Runtime:
    def __init__(
        self,
        csv_filepath: str,
        db_filepath: str,
        db_object_types: list[type[DBBaseModel]],
        db_echo: bool = True,
    ):
        self.reader: FileReader = FileReader(datafile=csv_filepath)
        self.dbhandler: DataBaseHandler = DataBaseHandler(
            dbfile=db_filepath,
            echo=db_echo,
            db_object_types=db_object_types,
        )
        self.evaluator: WealthEvaluator

    async def build_database(self) -> None:
        print("Creating Dropsources:\n")
        for source in self.reader.dropsources:
            print(f"\t{source}")
            await self.dbhandler.add_db_item(source, instant_commit=True)

        print("\nCreating Quantities:\n")
        for quantitiy in self.reader.quantities:
            print(f"\t{quantitiy}")
            await self.dbhandler.add_db_item(quantitiy, instant_commit=True)

        print("\nCreating Modifiers:\n")
        for modifier in self.reader.modifiers:
            print(f"\t{modifier}")
            await self.dbhandler.add_db_item(modifier, check_existence=False, instant_commit=True)

        print("\nCreating Items:\n")
        for item in self.reader.items:
            print(f"\t{item}")
            await self.dbhandler.add_db_item(item, instant_commit=True)

    async def add_player(self, params: InitParams, stats: Statistics) -> None:
        await self.dbhandler.add_db_item(params, instant_commit=True)
        await self.dbhandler.add_db_item(stats, instant_commit=True)

    async def get_items(self) -> list[Item]:
        return self.reader.items

    async def get_item(self, item_name: str) -> Optional[Item]:
        return await self.dbhandler.get_item(item_name)

    async def get_player_stats(self, player_name: str) -> Optional[Statistics]:
        return await self.dbhandler.get_player_stats(player_name)

    async def init_evaluator(self, stats: Optional[Statistics]) -> None:
        if not stats:
            raise ValueError("Required arg 'stats' is None.")
        self.evaluator = WealthEvaluator(
            stats=stats,
        )
