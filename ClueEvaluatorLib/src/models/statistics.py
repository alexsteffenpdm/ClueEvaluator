from __future__ import annotations

import pickle
import re
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

try:
    from ClueEvaluatorLib.src.models.base import DBBaseModel
except:  # noqa: E722
    from base import DBBaseModel  # type: ignore[no-redef]


class InitParams(DBBaseModel):
    player_name: str
    tier_4_luck: bool
    orlando: bool
    rebuild_db: bool = False

    async def as_db_item(self, db_model: BaseModel) -> BaseModel:
        return db_model(
            player_name=self.player_name,
            tier_4_luck=self.tier_4_luck,
            orlando=self.orlando,
            rebuild_db=self.rebuild_db,
        )

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def filter_statement(self) -> str:
        return f"SELECT * FROM initparams WHERE player_name == '{self.player_name}'"


class Statistics(DBBaseModel):
    player_name: str
    openend_caskets: int
    uniques: int
    broadcasts: int

    async def as_db_item(self, db_model: BaseModel) -> BaseModel:
        return db_model(
            player_name=self.player_name,
            openend_caskets=self.openend_caskets,
            uniques=self.uniques,
            broadcasts=self.broadcasts,
        )

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def filter_statement(self) -> str:
        return f"SELECT * FROM statistics WHERE player_name == '{self.player_name}'"

    async def reset(self) -> None:
        self.openend_caskets = 0
        self.uniques = 0
        self.broadcasts = 0


class WealthEvaluator(BaseModel):  # type: ignore
    start_time: Optional[datetime] = None
    total: int = 0
    stats: Statistics

    def model_post_init(self, __context: Any) -> None:
        self.start_time = datetime.now()
        super().model_post_init(__context)

    async def formatted_gp_value(self, value: int) -> str:
        return re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1,", "%d" % value)

    async def _make_rate(self, numerator: int) -> float:
        if self.stats.openend_caskets > 0:
            return numerator / self.stats.openend_caskets
        else:
            return 0

    async def hourly_rate(self) -> int:
        if self.start_time:
            endtime = datetime.now()
            duration = (self.start_time - endtime).seconds
            return int(self.total // (3600 / duration))
        return 0

    async def get_item_rates(self) -> dict[str, Any]:
        return {
            "unique_rate": f"{await self._make_rate(self.stats.uniques):.2%}",
            "broadcast_rate": f"{await self._make_rate(self.stats.broadcasts):.2%}",
        }

    async def get_money_rates(self) -> dict[str, Any]:
        return {
            "hourly": await self.formatted_gp_value(await self.hourly_rate()),
            "total": await self.formatted_gp_value(self.total),
            "average": await self.formatted_gp_value(int(await self._make_rate(self.total))),
        }

    async def get_info(self) -> dict[str, Any]:
        return {
            "item_rates": await self.get_item_rates(),
            "money_rates": await self.get_money_rates(),
            "stats": {
                "opened": f"{self.stats.openend_caskets}",
                "uniques": f"{self.stats.uniques}",
                "broadcasts": f"{self.stats.broadcasts}",
            },
        }

    async def reset(self) -> None:
        self.start_time = datetime.now()
        self.total = 0
        await self.stats.reset()
