from unittest.mock import patch
from urllib.parse import urlencode

from django.test import override_settings

from freezegun import freeze_time
from notifications_api_common.models import NotificationsConfig
from rest_framework import status
from rest_framework.test import APITestCase
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from objects.cloud_events.constants import ZAAK_GEKOPPELD, ZAAK_ONTKOPPELD
from objects.core.models import Reference
from objects.core.tests.factories import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
    ObjectTypeVersionFactory,
    ReferenceFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS
from .utils import reverse


@freeze_time("2018-09-07T00:00:00Z")
@override_settings(NOTIFICATIONS_DISABLED=False)
class SendNotifTestCase(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        ObjectTypeVersionFactory.create(object_type=cls.object_type)

        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def setUp(self):
        super().setUp()

        service, _ = Service.objects.update_or_create(
            api_root="https://notificaties-api.vng.cloud/api/v1/",
            defaults=dict(
                api_type=APITypes.nrc,
                client_id="test",
                secret="test",
                user_id="test",
                user_representation="Test",
            ),
        )
        config = NotificationsConfig.get_solo()
        config.notifications_api_service = service
        config.save()

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_create_object(self, mock_task):
        """
        Check if notifications will be send when Object is created
        """

        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()

        mock_task.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "create",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
            None,
        )

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_update_object(self, mock_task):
        """
        Check if notifications will be send when Object is created
        """

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])

        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        mock_task.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "update",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
            None,
        )

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_partial_update_object(self, mock_task):
        """
        Check if notifications will be send when Object is created
        """

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])

        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        mock_task.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "partial_update",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
            None,
        )

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_delete_object(self, mock_task):
        """
        Check if notifications will be send when Object is created
        """

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])
        full_url = f"http://testserver{url}"

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(url, **GEO_WRITE_KWARGS)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        mock_task.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": full_url,
                "resource": "object",
                "resourceUrl": full_url,
                "actie": "destroy",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
            None,
        )

    @patch("notifications_api_common.tasks.send_cloudevent.delay")
    @patch("notifications_api_common.viewsets.send_notification.delay")
    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        ENABLE_CLOUD_EVENTS=True,
        NOTIFICATIONS_SOURCE="open-object-test",
    )
    def test_send_cloudevent_adding_zaak(self, mock_notification, mock_event):
        url = reverse("object-list")
        data = {
            "type": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
                "references": [{"type": "zaak", "url": "https://example.com/zaak/1"}],
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()

        mock_event.assert_called_once()
        event = mock_event.call_args[0][0]
        self.assertEqual(event["type"], ZAAK_GEKOPPELD)
        self.assertTrue(
            event["data"]["label"].endswith(
                str(self.object_type.objectrecord_set.first())
            )
        )

        del event["data"]["label"]

        self.assertEqual(
            event["data"],
            {
                "zaak": "https://example.com/zaak/1",
                "linkTo": f"http://testserver/api/v2/objects/{data['uuid']}",
                "linkObjectType": "object",
            },
        )

        mock_notification.assert_called_once_with(
            {
                "kanaal": "objecten",
                "source": "open-object-test",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "create",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
            None,
        )

    @patch("notifications_api_common.tasks.send_cloudevent.delay")
    @patch("notifications_api_common.viewsets.send_notification.delay")
    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        ENABLE_CLOUD_EVENTS=True,
        NOTIFICATIONS_SOURCE="open-object-test",
    )
    def test_send_cloudevents_changing_zaak(self, mock_notification, mock_event):
        obj = ObjectFactory.create(object_type=self.object_type)
        ref = ReferenceFactory.create(
            type="zaak", url="https://example.com/zaak/1", record__object=obj
        )
        ReferenceFactory.create(
            type="zaak", url="https://example.com/zaak/2", record=ref.record
        )

        url = reverse("object-detail", args=[obj.uuid])

        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
                "references": [
                    {"type": "zaak", "url": "https://example.com/zaak/2"},
                    {"type": "zaak", "url": "https://example.com/zaak/3"},
                ],
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        self.assertEqual(mock_event.call_count, 2)

        koppel_event = mock_event.call_args_list[0][0][0]
        self.assertEqual(koppel_event["type"], ZAAK_GEKOPPELD)
        self.assertTrue(
            koppel_event["data"]["label"].endswith(
                str(self.object_type.objectrecord_set.last())
            )
        )

        del koppel_event["data"]["label"]

        self.assertEqual(
            koppel_event["data"],
            {
                "zaak": "https://example.com/zaak/3",
                "linkTo": f"http://testserver/api/v2/objects/{data['uuid']}",
                "linkObjectType": "object",
            },
        )

        ontkoppel_event = mock_event.call_args_list[1][0][0]
        self.assertEqual(ontkoppel_event["type"], ZAAK_ONTKOPPELD)
        self.assertEqual(
            ontkoppel_event["data"],
            {
                "zaak": "https://example.com/zaak/1",
                "linkTo": f"http://testserver/api/v2/objects/{data['uuid']}",
                "linkObjectType": "object",
            },
        )

        mock_notification.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": f"http://testserver{url}",
                "resource": "object",
                "resourceUrl": f"http://testserver{url}",
                "actie": "partial_update",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
                "source": "open-object-test",
            },
            None,
        )

    @patch("notifications_api_common.tasks.send_cloudevent.delay")
    @patch("notifications_api_common.viewsets.send_notification.delay")
    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        ENABLE_CLOUD_EVENTS=True,
        NOTIFICATIONS_SOURCE="open-object-test",
    )
    def test_send_cloudevents_deleting_object(self, mock_notification, mock_event):
        obj = ObjectFactory.create(object_type=self.object_type)
        ref = ReferenceFactory.create(
            type="zaak", url="https://example.com/zaak/1", record__object=obj
        )
        ReferenceFactory.create(
            type="zaak", url="https://example.com/zaak/2", record=ref.record
        )

        url = reverse("object-detail", args=[obj.uuid])

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(url, *GEO_WRITE_KWARGS)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        assert not Reference.objects.exists()

        self.assertEqual(mock_event.call_count, 2)

        events = [args[0][0] for args in mock_event.call_args_list]

        assert {event["type"] for event in events} == {ZAAK_ONTKOPPELD}
        assert {event["data"]["linkTo"] for event in events} == {
            f"http://testserver{url}"
        }
        assert {event["data"]["linkObjectType"] for event in events} == {"object"}

        assert {event["data"]["zaak"] for event in events} == {
            "https://example.com/zaak/1",
            "https://example.com/zaak/2",
        }

        mock_notification.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": f"http://testserver{url}",
                "resource": "object",
                "resourceUrl": f"http://testserver{url}",
                "actie": "destroy",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
                "source": "open-object-test",
            },
            None,
        )

    @patch("notifications_api_common.tasks.send_cloudevent.delay")
    @patch("notifications_api_common.viewsets.send_notification.delay")
    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        ENABLE_CLOUD_EVENTS=True,
        NOTIFICATIONS_SOURCE="open-object-test",
    )
    def test_send_cloudevents_deleting_object_archiving_only_zaak(
        self, mock_notification, mock_event
    ):
        "Open Archiefbeheer DELETEs with zaak queryparam when archiving"

        zaak_1 = "https://example.com/zaak/1"

        obj = ObjectFactory.create(object_type=self.object_type)
        ReferenceFactory.create(type="zaak", url=zaak_1, record__object=obj)

        url = reverse("object-detail", args=[obj.uuid])

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(
                f"{url}?{urlencode({'zaak': zaak_1})}", *GEO_WRITE_KWARGS
            )

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        assert not Reference.objects.exists()

        self.assertEqual(mock_event.call_count, 1)

        events = [args[0][0] for args in mock_event.call_args_list]

        assert {event["type"] for event in events} == {ZAAK_ONTKOPPELD}
        assert {event["data"]["linkTo"] for event in events} == {
            f"http://testserver{url}"
        }
        assert {event["data"]["linkObjectType"] for event in events} == {"object"}

        assert {event["data"]["zaak"] for event in events} == {
            "https://example.com/zaak/1"
        }

        mock_notification.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": f"http://testserver{url}",
                "resource": "object",
                "resourceUrl": f"http://testserver{url}",
                "actie": "destroy",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
                "source": "open-object-test",
            },
            None,
        )

    @patch("notifications_api_common.tasks.send_cloudevent.delay")
    @patch("notifications_api_common.viewsets.send_notification.delay")
    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        ENABLE_CLOUD_EVENTS=True,
        NOTIFICATIONS_SOURCE="open-object-test",
    )
    def test_send_cloudevents_deleting_object_archiving_a_zaak(
        self, mock_notification, mock_event
    ):
        "Open Archiefbeheer DELETEs with zaak queryparam when archiving"

        zaak_1 = "https://example.com/zaak/1"

        obj = ObjectFactory.create(object_type=self.object_type)
        ref = ReferenceFactory.create(type="zaak", url=zaak_1, record__object=obj)
        ReferenceFactory.create(
            type="zaak", url="https://example.com/zaak/2", record=ref.record
        )

        url = reverse("object-detail", args=[obj.uuid])

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(
                f"{url}?{urlencode({'zaak': zaak_1})}", *GEO_WRITE_KWARGS
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        assert {ref.url for ref in Reference.objects.all()} == {
            "https://example.com/zaak/2"
        }

        self.assertEqual(mock_event.call_count, 1)

        event = mock_event.call_args_list[0][0][0]

        assert event["type"] == ZAAK_ONTKOPPELD
        assert event["data"]["linkTo"] == f"http://testserver{url}"

        assert event["data"]["linkObjectType"] == "object"

        assert event["data"]["zaak"] == "https://example.com/zaak/1"

        # check correct notification

        mock_notification.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": f"http://testserver{url}",
                "resource": "object",
                "resourceUrl": f"http://testserver{url}",
                "actie": "update",  # wasn't destroyed, but changed!
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
                "source": "open-object-test",
            },
            None,
        )

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        ENABLE_CLOUD_EVENTS=False,
    )
    @patch("notifications_api_common.tasks.send_cloudevent.delay")
    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_no_notifications_sent_when_disabled(self, mock_notification, mock_events):
        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
                "references": [{"type": "zaak", "url": "https://example.com/zaak/1"}],
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, data, **GEO_WRITE_KWARGS)
            object_url = response.json()["url"]
            put_reponse = self.client.put(object_url, data, **GEO_WRITE_KWARGS)
            delete_response = self.client.delete(object_url)

        assert put_reponse.status_code == status.HTTP_200_OK
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        assert mock_notification.call_count == 3
        assert mock_events.call_args_list == []
