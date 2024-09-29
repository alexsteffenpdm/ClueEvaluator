from __future__ import annotations

import copy
import os
import pathlib
from functools import lru_cache
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

import ClueEvaluatorLib.src.models.items as ItemModels
import ClueEvaluatorLib.src.models.statistics as StatisticModels
from ClueEvaluatorLib.src.models.base import Configuration
from ClueEvaluatorLib.src.models.runtime import Runtime

app = FastAPI(debug=True)


# Set up allowed origins
origins = [
    "http://localhost:3000",  # Frontend URL
    "http://localhost:8000",  # Backend URL
    # Add other URLs as needed
    "null",
]

# Add CORS middleware to allow WebSocket requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SETTINGS: StatisticModels.InitParams
RUNTIME: Runtime

CONFIG: Configuration
CONFIG_PATH = os.path.join(
    pathlib.Path(
        __file__,
    ).parent.parent.absolute(),
    "config",
    "config.ini",
)


def config_status() -> bool:
    return os.path.exists(CONFIG_PATH)


OBJECT_TYPES = [
    StatisticModels.InitParams,
    StatisticModels.Statistics,
    ItemModels.ItemQuantity,
    ItemModels.DropSources,
    ItemModels.ItemModifiers,
    ItemModels.Item,
]


@app.get("/")  # type: ignore[misc]
def read_root() -> dict[str, Any]:
    return {"Hello": "World"}


@app.post("/configure/")  # type: ignore[misc]
async def configure(configuration_parameters: dict[str, dict[str, str]]) -> bool:
    global CONFIG_PATH, CONFIG
    with open(CONFIG_PATH) as fp:
        for section, vars in configuration_parameters.items():
            fp.write(f"[{section}]\n")
            [fp.write(f"{name}={data}\n") for name, data in vars.items()]
            fp.write("\n")

    CONFIG = Configuration()
    CONFIG.from_config_file(CONFIG_PATH)
    return True


@app.post("/initialize/")  # type: ignore[misc]
async def initialize_plugin(parameters: StatisticModels.InitParams) -> dict[str, Any]:
    global SETTINGS, RUNTIME, CONFIG
    # if not config_status():
    #     raise HTTPException(
    #         status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
    #         detail=(
    #             "Initialize failed: Configuration is missing," " please use the Configurator first.",
    #         ),
    #     )
    # CONFIG = Configuration()
    # CONFIG.from_config_file(CONFIG_PATH)

    SETTINGS = copy.deepcopy(parameters)
    if SETTINGS is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Initialize failed: Could not create Plugin object.",
        )
    try:
        if parameters.rebuild_db:
            if os.path.exists("C:\\Development\\RS3\\ClueEvaluator\\ClueEvaluatorLib\\data\\test.db"):
                os.remove("C:\\Development\\RS3\\ClueEvaluator\\ClueEvaluatorLib\\data\\test.db")

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Initialize failed: "
                "Could not recreate database as it is already in use. "
                "If you want to rebuild the database, "
                "you must restart the plugin. "
            ),
        )

    RUNTIME = Runtime(
        csv_filepath="C:\\Development\\RS3\\tinkers\\testcsv.csv",
        db_filepath="C:\\Development\\RS3\\ClueEvaluator\\ClueEvaluatorLib\\data\\test.db",
        db_object_types=OBJECT_TYPES,
        db_echo=False,
    )
    if parameters.rebuild_db:
        print("Recreating Models")
        await RUNTIME.reader._get_data()
        await RUNTIME.dbhandler.create_all_models(object_types=OBJECT_TYPES)
        print("Rebuilding Database")
        await RUNTIME.build_database()

        stats = StatisticModels.Statistics(
            player_name=parameters.player_name,
            openend_caskets=0,
            uniques=0,
            broadcasts=0,
        )

        await RUNTIME.add_player(params=parameters, stats=stats)
    await RUNTIME.init_evaluator(
        await RUNTIME.get_player_stats(parameters.player_name),
    )
    return {
        "message": "Initialization ran successful.",
    }


@lru_cache(maxsize=5)
@app.get("/player/name")  # type: ignore[misc]
async def get_player_name() -> dict[str, Any]:

    if SETTINGS:
        return {
            "message": SETTINGS.player_name,
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Initialization not done yet. Could not retrieve player name.",
    )


@app.get("/python/items")  # type: ignore[misc]
async def get_python_items() -> list[ItemModels.Item]:
    return await RUNTIME.get_items()


@lru_cache(maxsize=5)
@app.get("/items/")  # type: ignore[misc]
async def get_item(item_name: str) -> Optional[ItemModels.Item]:
    item: Optional[ItemModels.Item] = await RUNTIME.get_item(item_name)
    if item:
        return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not find the requested item.",
    )


@lru_cache(maxsize=5)
@app.get("/player/statistics")  # type: ignore[misc]
async def get_statistics(player_name: str) -> Optional[StatisticModels.Statistics]:
    stats: Optional[StatisticModels.Statistics] = await RUNTIME.get_player_stats(
        player_name,
    )
    if stats:
        return stats
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Could not find statistics for the given player.",
    )


@app.get("/update/wealthevaluator")  # type: ignore[misc]
async def update_evaluator() -> dict[str, Any]:
    if RUNTIME.evaluator:
        return await RUNTIME.evaluator.get_info()

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Initialization not done yet. Could not retrieve player name.",
    )
