from __future__ import annotations

from typing import Any

from pydantic import BaseModel

try:
    import ClueEvaluatorLib.src.models.items as ItemModels
except:  # noqa: E722
    import items as ItemModels  # type: ignore[no-redef]

import csv


def str2bool(v: str) -> bool:
    if v.lower() in ("false", "f", "0", "no"):
        return False
    elif v.lower() in ("true", "t", "1", "yes"):
        return True
    raise ValueError("Unknown string to convert to boolan value")


class FileReader(BaseModel):  # type: ignore
    datafile: str
    dropsources: list[ItemModels.DropSources] = []
    quantities: list[ItemModels.ItemQuantity] = []
    modifiers: list[ItemModels.ItemModifiers] = []
    items: list[ItemModels.Item] = []

    async def _make_dropsources(self, data: str) -> list[ItemModels.DropSources]:
        instances = []

        for instance in data.split("-"):
            parts = instance.split("@")
            new_instance = ItemModels.DropSources(
                name=str(parts[0]),
                rate=str(parts[1]),
            )
            if new_instance not in instances:
                instances.append(new_instance)

        return instances

    async def _make_quantity(self, data: str) -> ItemModels.ItemQuantity:
        return ItemModels.ItemQuantity(
            minquantity=int(data.split("-")[0]),
            maxquantity=int(data.split("-")[1]),
        )

    async def _make_modifiers(self, data: str) -> ItemModels.ItemModifiers:
        parts = data.split(",")
        quantity = parts[0].split("=", 1)[1]
        sources = parts[1].split("=", 1)[1]

        return ItemModels.ItemModifiers(
            itemquantity=await self._make_quantity(data=quantity),
            dropsources=await self._make_dropsources(data=sources),
        )

    def _item_make_internal_name(self, name: str) -> str:
        return (
            name.replace(
                " ",
                "_",
            )
            .lower()
            .capitalize()
        )

    async def _make_objects(self, data: dict[str, Any]) -> None:
        object_sources: list[ItemModels.DropSources] = await self._make_dropsources(data["sources"])
        [self.dropsources.append(source) for source in object_sources if source not in self.dropsources]  # type: ignore[func-returns-value]

        object_quantitiy: ItemModels.ItemQuantity = await self._make_quantity(data["quantity"])
        if object_quantitiy not in self.quantities:
            self.quantities.append(object_quantitiy)

        object_modifiers: ItemModels.ItemModifiers
        if not data["modifiers"] == "none":
            object_modifiers = await self._make_modifiers(data["modifiers"])
            if object_modifiers not in self.modifiers:
                self.modifiers.append(object_modifiers)

        item: ItemModels.Item = ItemModels.Item(
            display_name=data["display_name"],
            itemquantity=object_quantitiy,
            is_unique=str2bool(data["is_unique"]),
            noted=str2bool(data["noted"]),
            is_broadcast=str2bool(data["is_broadcast"]),
            dropsources=object_sources,
            droptable=data["table"],
            price=int(data["price"]) if data["price"] != "None" else None,
            itemmodifiers=object_modifiers,
            image_id=int(data["image_id"]),
            category=data["category"],
        )

        if item not in self.items:
            self.items.append(item)

    async def _get_data(self) -> None:

        with open(self.datafile, newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
            for row in enumerate(reader):
                print(f"Processing row {row[0]}")
                await self._make_objects(row[1])


if __name__ == "__main__":
    reader = FileReader(datafile="C:\\Development\\RS3\\test2csv.csv")

    print("Priting Dropsources:\n")
    for source in reader.dropsources:
        print(f"\t{source}")

    print("\nPrinting Quantities:\n")
    for quantitiy in reader.quantities:
        print(f"\t{quantitiy}")

    print("\nPrinting Modifiers:\n")
    for modifier in reader.modifiers:
        print(f"\t{modifier}")

    print("\nPrinting Items:\n")
    for item in reader.items:
        print(f"\t{item}")
