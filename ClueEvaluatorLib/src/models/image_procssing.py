from __future__ import annotations

import mss.windows

try:
    from ClueEvaluatorLib.src.models.base import ScreenSection
except:  # noqa: E722
    from base import ScreenSection  # type: ignore[no-redef]

from typing import Any

import cv2
import mss.tools
import numpy as np
import pytesseract
from cv2.typing import MatLike

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ImageRecongition:
    tesseract_config: str = r"--oem 3 --psm 6"
    mss_context: mss.windows.MSS = mss.mss()

    async def _set_image_threshold(self, image: MatLike, thresh: float, max: float, type: int) -> None:
        _, thresh_image = cv2.threshold(image, thresh, max, type)
        image = thresh_image

    async def _image_encoding(self, image: np.ndarray, code: int) -> MatLike:
        return cv2.cvtColor(image, code=code)

    async def _rgb_image(self, image: np.ndarray) -> None:
        image = await self._image_encoding(image, cv2.COLOR_BGR2RGB)

    async def _grayscale_image(self, image: np.ndarray) -> None:
        image = await self._image_encoding(image, cv2.COLOR_BGR2GRAY)

    async def _get_text(self, image: MatLike) -> Any:
        return pytesseract.image_to_string(image, config=self.tesseract_config)

    async def _mss_get_image(self, image_params: ScreenSection) -> np.ndarray:
        with self.mss_context as context:
            return np.array(context.grab(image_params.mss_monitor_dict()))

    async def _process_image(self, image: MatLike) -> Any:
        await self._set_image_threshold(image, 150, 255, cv2.THRESH_BINARY)
        return await self._get_text(image)

    async def get_clue_reward_value(self, image_params: ScreenSection) -> str:
        image: MatLike = await self._mss_get_image(image_params)
        await self._rgb_image(image)
        return await self._process_image(image)

    async def get_clue_reward_items(self, image_params: ScreenSection) -> str:
        image: MatLike = await self._mss_get_image(image_params)
        await self._grayscale_image(image)
        return await self._process_image(image)


async def _main() -> None:
    from datetime import datetime

    start = datetime.now()
    screensec = ScreenSection(
        top=973,
        left=1004,
        width=312,
        height=24,
    )

    recognizer = ImageRecongition()
    out = await recognizer.get_clue_reward_value(screensec)
    end = datetime.now()
    print(out)
    difference = end - start
    difference_in_milliseconds = difference.total_seconds() * 1000

    print(f"Processing time: {difference_in_milliseconds:.2f} ms")


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(_main())
    loop.run_forever()
    loop.close()
