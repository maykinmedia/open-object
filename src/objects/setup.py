"""
Bootstrap the environment.

Load the secrets from the .env file and store them in the environment, so
they are available for Django settings initialization.

.. warning::

    do NOT import anything Django related here, as this file needs to be loaded
    before Django is initialized.
"""

import os
import warnings

from django.conf import settings

import structlog
from dotenv import load_dotenv
from maykin_common.otel import setup_otel

logger = structlog.stdlib.get_logger(__name__)

_env_setup_done = False


def setup_env():
    global _env_setup_done
    if _env_setup_done:
        return

    # load the environment variables containing the secrets/config
    dotenv_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env")
    load_dotenv(dotenv_path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "objects.conf.dev")
    if "OTEL_SERVICE_NAME" not in os.environ:
        warnings.warn(
            "No OTEL_SERVICE_NAME environment variable set, using a default. "
            "You should set a (distinct) value for each component (web, worker...)",
            RuntimeWarning,
            stacklevel=2,
        )
        os.environ.setdefault("OTEL_SERVICE_NAME", "openobject")

    setup_otel()

    structlog.contextvars.bind_contextvars(source="app")

    monkeypatch_requests()

    _env_setup_done = True


def monkeypatch_requests():
    """
    Add a default timeout for any requests calls.

    """
    try:
        from requests import Session
    except ModuleNotFoundError:
        logger.debug("Attempt to patch requests, but the library is not installed")
        return

    if hasattr(Session, "_original_request"):
        logger.debug(
            "Session is already patched OR has an ``_original_request`` attribute."
        )
        return

    Session._original_request = Session.request

    def new_request(self, *args, **kwargs):
        kwargs.setdefault("timeout", settings.REQUESTS_DEFAULT_TIMEOUT)
        return self._original_request(*args, **kwargs)

    Session.request = new_request
