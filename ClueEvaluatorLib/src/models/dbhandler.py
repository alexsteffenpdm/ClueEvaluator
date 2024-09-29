from __future__ import annotations

import pickle
from typing import Any, Optional

from pydantic import create_model
from sqlalchemy import inspect, text
from sqlmodel import Field, Session, SQLModel, create_engine, select

try:
    from ClueEvaluatorLib.src.models.base import DBBaseModel
    from ClueEvaluatorLib.src.models.items import Item
    from ClueEvaluatorLib.src.models.statistics import Statistics
    from ClueEvaluatorLib.src.models.util import str2bool

except:  # noqa: E722
    from statistics import Statistics  # type: ignore[no-redef,attr-defined]

    from base import DBBaseModel  # type: ignore[no-redef]
    from items import Item  # type: ignore[no-redef]
    from util import str2bool  # type: ignore[no-redef]


class DataBaseHandler:
    def __init__(self, dbfile: str, echo: bool = True, db_object_types: list[type[DBBaseModel]] = []):
        self.dbfile = dbfile
        self.dbecho = echo
        self.dburl = f"sqlite:///{dbfile}"
        self.engine = create_engine(self.dburl, echo=self.dbecho)
        self.session = Session(self.engine)
        self.models: dict[str, type[DBBaseModel]] = {}
        self.inspector = inspect(self.engine)
        self.db_object_types: list[type[DBBaseModel]] = db_object_types

    async def check_table_exists(self, table_name: str) -> Any:
        return await self.inspector.has_table(table_name)

    async def get_all_table_items(self, model: DBBaseModel) -> Any:
        with self.session as session:
            return await session.exec(select(model)).all()

    async def reload_inspector(self) -> None:
        self.inspector = inspect(self.engine)

    async def make_field_definitions(self, model: DBBaseModel) -> dict[str, Any]:
        model_fields = model.model_fields
        field_definitions = {
            "id": (int, Field(default=None, primary_key=True)),
        }
        await self.reload_inspector()
        table_names = self.inspector.get_table_names()
        for name, info in model_fields.items():
            print(
                f"\tCreating field definition for {name} with annotation: {info.annotation}",
            )

            if name not in table_names:
                field_definitions[name] = (info.annotation, ...)
            else:
                print(
                    f"Setting foreign key for {model.__name__} attribute: {name}",
                )
                field_definitions[name] = (str, ...)  # type: ignore[assignment]
        return field_definitions

    async def create_all_models(self, object_types: Any) -> None:
        for object_type in object_types:
            model_name = f"{object_type.__name__}"
            print(f"Creating db_model for  {model_name} ...")
            self.models[f"{model_name.lower()}_model"] = await self.create_model(object_type)
            print(f"Successfully create db_model for {model_name}")
            SQLModel.metadata.create_all(self.engine)

    async def create_model(self, model: Any) -> Any:
        field_definitions = await self.make_field_definitions(model)
        table_name = str(model.__name__)
        return create_model(
            table_name,
            __base__=SQLModel,
            __cls_kwargs__={"table": True},
            **field_definitions,
        )

    async def add_db_item(
        self, item: DBBaseModel, check_existence: bool = True, instant_commit: bool = True
    ) -> None:
        db_item = await item.as_db_item(db_model=self.models[f"{item.__class__.__name__.lower()}_model"])

        if check_existence:
            if not await self.check_existence(item):
                self.session.add(db_item)
        else:
            self.session.add(db_item)

        if instant_commit:
            self.session.commit()

    async def check_existence(self, item: DBBaseModel) -> bool:
        return self.session.exec(text(item.filter_statement())).first() is not None

    async def get_item(self, item_name: str) -> Optional[Item]:

        result = self.session.exec(
            text(f"SELECT * FROM item WHERE display_name == '{item_name}'"),
        ).first()
        if result:
            return Item(
                display_name=result[1],
                internal_name=result[2],
                itemquantity=pickle.loads(result[3]),
                is_unique=str2bool(str(result[4])),
                is_broadcast=str2bool(str(result[5])),
                noted=str2bool(str(result[6])),
                dropsources=[pickle.loads(instance) for instance in pickle.loads(result[7])],
                droptable=result[8],
                price=result[9],
                itemmodifiers=pickle.loads(pickle.loads(result[10])),
                image_id=result[11],
                category=result[12],
            )
        return None

    async def get_player_stats(self, player_name: str) -> Optional[Statistics]:
        result = self.session.exec(
            text(
                f"SELECT * FROM statistics WHERE player_name == '{player_name}'",
            ),
        ).first()
        if result:
            return Statistics(
                player_name=result[1],
                openend_caskets=result[2],
                uniques=result[3],
                broadcasts=result[4],
            )
        return None
