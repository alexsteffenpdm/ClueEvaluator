from __future__ import annotations

try:
    from ClueEvaluatorLib.src.models.base import DBBaseModel
except:  # noqa: E722
    from base import DBBaseModel  # type: ignore[no-redef]

import pickle
from typing import Any, Optional

import requests
from pydantic import BaseModel


class ItemQuantity(DBBaseModel):
    minquantity: int
    maxquantity: int

    async def as_db_item(self, db_model: DBBaseModel) -> type[ItemQuantity]:
        return db_model(
            minquantity=self.minquantity,
            maxquantity=self.maxquantity,
        )

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def filter_statement(self) -> str:
        return f"SELECT * FROM itemquantity WHERE minquantity == {self.minquantity} AND maxquantity == {self.maxquantity}"


class DropSources(DBBaseModel):
    name: str
    rate: str
    decimal_rate: Optional[float] = None

    def model_post_init(self, __context: Any) -> None:
        self._make_decimal_rate()
        super().model_post_init(__context)

    def __str__(self) -> str:
        return f'DropSource(name="{self.name}", rate={self.rate})'

    def __repr__(self) -> str:
        return self.__str__()

    async def as_db_item(self, db_model: BaseModel) -> type[DropSources]:
        return db_model(
            name=self.name,
            rate=self.rate,
            decimal_rate=self.decimal_rate,
        )

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def filter_statement(self) -> str:
        return f"SELECT * FROM dropsources WHERE name == '{self.name}' AND rate == '{self.rate}'"

    def _make_decimal_rate(self) -> None:
        self.decimal_rate = round(float(eval(self.rate)), 9)  #


class ItemModifiers(DBBaseModel):
    itemquantity: Optional[ItemQuantity]
    dropsources: Optional[list[DropSources]]

    async def as_db_item(self, db_model: BaseModel) -> type[ItemModifiers]:
        return db_model(
            itemquantity=self.itemquantity.serialize() if self.itemquantity else None,
            dropsources=(
                pickle.dumps([source.serialize() for source in self.dropsources])
                if self.dropsources
                else None
            ),
        )

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def filter_statement(self) -> str:
        itemquantity_bstr: str = ""
        if not self.itemquantity:
            raise ValueError("Cannot build filter statement with 'itemquantity = None'")
        else:
            itemquantity_bstr = str(pickle.dumps(self.itemquantity.serialize()))
        return f"SELECT * FROM itemmodifiers WHERE itemquantity == {itemquantity_bstr}"


class Item(DBBaseModel):
    display_name: str
    internal_name: Optional[str] = None
    itemquantity: ItemQuantity
    is_unique: bool
    is_broadcast: bool
    noted: bool
    dropsources: list[DropSources]
    droptable: str
    price: Optional[int]
    itemmodifiers: Optional[ItemModifiers] = None
    image_id: int
    category: str

    async def make_internal_name(self) -> None:
        self.internal_name = (
            self.display_name.replace(
                " ",
                "_",
            )
            .lower()
            .capitalize()
        )

    async def get_price_from_wiki(self, update_price: bool = True) -> None:
        if self.internal_name is None:
            await self.make_internal_name()
        dummy_internal_name = "Armadyl_page_1"
        request = requests.get(
            f"https://www.runescape.wiki/w/Exchange:{dummy_internal_name}",
        )
        # request = requests.get(f"https://www.runescape.wiki/w/Exchange:{self.internal_name}")
        _price = int(
            str(request.content).split('id="GEPrice">')[1].split("<", 1)[0].replace(",", ""),
        )
        if update_price:
            self.price = _price

    def get_image_url(self) -> str:
        return f"https://runescape.wiki/images/{self.internal_name}.png?{self.image_id}"

    async def model_post_init(self, __context: Any) -> None:
        await self.make_internal_name()
        await self.get_price_from_wiki(update_price=self.price is None)
        await super().model_post_init(__context)

    async def as_db_item(self, db_model: BaseModel) -> BaseModel:
        return db_model(
            display_name=self.display_name,
            internal_name=self.internal_name,
            itemquantity=self.itemquantity.serialize(),
            is_unique=self.is_unique,
            is_broadcast=self.is_broadcast,
            noted=self.noted,
            dropsources=(
                pickle.dumps([source.serialize() for source in self.dropsources])
                if self.dropsources
                else None
            ),
            droptable=self.droptable,
            price=self.price,
            itemmodifiers=(pickle.dumps(self.itemmodifiers.serialize()) if self.itemmodifiers else None),
            image_id=self.image_id,
            category=self.category,
        )

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def filter_statement(self) -> str:
        return f"SELECT * FROM item WHERE display_name == '{self.display_name}'"
