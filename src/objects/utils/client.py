from uuid import UUID

import requests
from zgw_consumers.client import build_client
from zgw_consumers.nlx import NLXClient
from zgw_consumers.service import pagination_helper
from zgw_consumers.utils import PaginatedResponseData


class ObjecttypesClient(NLXClient):
    def _get_paginated(
        self,
        endpoint: str,
        page: int | None = None,
        page_size: int | None = None,
        query_params: dict[str, str | int] | None = None,
    ):
        query_params = query_params or {}
        if page is None and page_size is None:
            response = self.get(endpoint, params=query_params)
            response.raise_for_status()
            data: PaginatedResponseData = response.json()
            all_data = pagination_helper(self, data)
            return list(all_data)

        if page is not None:
            query_params["page"] = page
        if page_size is not None:
            query_params["pageSize"] = page_size

        response = self.get(endpoint, params=query_params)
        response.raise_for_status()
        return response.json()["results"]

    @property
    def can_connect(self) -> bool:
        try:
            response = self.get("objecttypes")
            response.raise_for_status()
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_objecttypes(
        self,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[dict[str, object]]:
        return self._get_paginated(
            "objecttypes",
            page=page,
            page_size=page_size,
        )

    def get_objecttype(
        self,
        objecttype_uuid: str | UUID,
    ) -> dict[str, object]:
        response = self.get(f"objecttypes/{objecttype_uuid}")
        response.raise_for_status()
        return response.json()

    def list_objecttype_versions(
        self,
        objecttype_uuid: str | UUID,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[dict[str, object]]:
        return self._get_paginated(
            f"objecttypes/{objecttype_uuid}/versions", page=page, page_size=page_size
        )

    def get_objecttype_version(
        self,
        objecttype_uuid: str | UUID,
        version: int,
    ) -> dict[str, object]:
        response = self.get(f"objecttypes/{objecttype_uuid}/versions/{version}")
        response.raise_for_status()
        return response.json()

    def get_objecttypes_api_version(self) -> str | None:
        response = self.head("")
        response.raise_for_status()
        return response.headers.get("api-version")


def get_objecttypes_client(service) -> ObjecttypesClient:
    assert service is not None
    return build_client(service, client_factory=ObjecttypesClient)
