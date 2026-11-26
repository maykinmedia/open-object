from django.conf import settings

from celery import shared_task
from notifications_api_common.cloudevents import process_cloudevent

from objects.core.constants import ReferenceType
from objects.core.models import ObjectRecord, Reference

from .constants import ZAAK_GEKOPPELD, ZAAK_ONTKOPPELD


@shared_task
def send_zaak_events(object_record_id: int, object_url: str):
    """Send all zaak gekoppeld/ontkoppeld

    In order to not slow down the object API endpoint with extra queries and
    multiple cloudevent schedules, this is done in a task.
    """
    if not settings.ENABLE_CLOUD_EVENTS:
        return

    try:
        record = (
            ObjectRecord.objects.select_related("object")
            .prefetch_related("references")
            .get(pk=object_record_id)
        )
    except ObjectRecord.DoesNotExist:  # pragma: no cover
        return

    object = record.object
    label = f"{object.object_type.name} {record}"

    current: set[str] = {
        ref.url for ref in record.references.all() if ref.type == ReferenceType.zaak
    }
    previous: set[str] = {
        ref.url
        for ref in Reference.objects.filter(
            type=ReferenceType.zaak,
            record__object__pk=object.pk,
            record__index=record.index - 1,
        )
    }

    gekoppeld: set[str] = current - previous
    ontkoppeld: set[str] = previous - current

    for zaak_url in gekoppeld:
        process_cloudevent(
            ZAAK_GEKOPPELD,
            data={
                "zaak": zaak_url,
                "linkTo": object_url,
                "linkObjectType": "object",
                "label": label,
            },
        )

    for zaak_url in ontkoppeld:
        process_cloudevent(
            ZAAK_ONTKOPPELD,
            data={
                "zaak": zaak_url,
                "linkTo": object_url,
                "linkObjectType": "object",
                # label is not used, it's pure display and not needed for removal
            },
        )
