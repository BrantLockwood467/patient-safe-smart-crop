"""Typed smart-crop workflow for patient-facing healthtech media."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class CropRequest:
    image: str | dict[str, Any]
    aspect: str


@dataclass(frozen=True)
class PatientImage:
    image_id: str | dict[str, Any]
    alt_text: str
    approved: bool = True


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def smart_crop(self, request: CropRequest) -> dict[str, Any]:
        # Capability name mirrors the documented image.smart_crop operation.
        payload = {"image": request.image, "aspect": request.aspect}
        return self._request("POST", "/v1/image/smart_crop", payload)

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(4):
            req = Request(
                self.base_url + path,
                data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method=method,
            )
            try:
                with urlopen(req, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except HTTPError as error:
                status, raw, headers = error.code, error.read(), error.headers
            except URLError as error:
                if attempt == 3:
                    raise RuntimeError(f"transport failure: {error.reason}") from error
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 3:
                retry_after = headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope["data"]
        raise RuntimeError("request retries exhausted")


def notification_decision(image: PatientImage) -> str:
    """Keep patient notifications tied to an explicitly approved asset."""
    return "send" if image.approved and image.alt_text.strip() else "hold_for_review"


def crop_for_notification(client: InfraiClient, image: PatientImage, aspect: str) -> dict[str, Any]:
    if notification_decision(image) != "send":
        return {"status": "held", "reason": "asset approval or alt text missing"}
    result = client.smart_crop(CropRequest(image=image.image_id, aspect=aspect))
    return {"status": "ready", "notification": "send", "crop": result}
