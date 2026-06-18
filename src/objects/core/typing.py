from __future__ import annotations

from collections.abc import MutableMapping, Sequence

type JSONPrimitive = str | int | float | bool | None

type JSONValue = JSONPrimitive | JSONObject | Sequence[JSONValue]

type JSONObject = MutableMapping[str, JSONValue]
