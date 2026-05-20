import json

import hypothesis.strategies as st
import jsonschema_specifications
from hypothesis.extra.django import from_model
from hypothesis_jsonschema import from_schema

from objects.core.models import ObjectType, ObjectTypeVersion

from ..utils import check_json_schema


def _valid_schema(json_value):
    try:
        check_json_schema(json_value)
    except Exception:  # pragma: no cover
        return False
    else:
        # no escaped null-bytes PG JSONFields can't handle them
        return r"\u0000" not in json.dumps(json_value)


def jsonschemas():
    "Hypothesesis strategy that generates valid jsonschemata."
    # from_schema doesn't resolve $dynamicRef (yet), which the 2020 draft meta schema uses
    meta_schema = "https://json-schema.org/draft/2019-09/schema"
    return st.one_of(
        st.booleans(),
        st.just({}),
        (
            from_schema(
                jsonschema_specifications.REGISTRY[meta_schema].contents,  # type: ignore
            )
            .map(
                lambda schema: schema | {"$schema": meta_schema}
                if isinstance(schema, dict)
                else schema
            )
            .filter(_valid_schema)
        ),
    )


@st.composite
def objecttypes(
    draw: st.DrawFn, *, min_versions: int = 0, max_versions: int | None = None
) -> ObjectType:
    # postgres can't store

    object_type = draw(
        from_model(
            ObjectType,
            is_imported=st.just(False),
            contact_email=st.just("") | st.emails(),  # optional email
        )
    )
    # for better scr
    schemata = jsonschemas()
    schema = draw(schemata)

    # create some versions
    draw(
        st.lists(
            from_model(
                ObjectTypeVersion,
                object_type=st.just(object_type),
                json_schema=st.one_of(
                    st.just(schema),  # re-use same
                    schemata,  # change to a new schema
                ),
                # hypothesis infers the bounds correctly, but also tries 0
                # and will bump into the auto gen going out of bounds
                version=st.integers(min_value=1, max_value=(1 << 15) - 1),
            ),
            min_size=min_versions,
            max_size=max_versions,
        )
    )
    return object_type
