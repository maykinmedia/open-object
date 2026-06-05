import os

from upgrade_check.constraints import (
    CommandCheck,
    UpgradeCheck,
    UpgradePaths,
    VersionRange,
)

os.environ["_USE_STRUCTLOG"] = "True"

from django.core.exceptions import ImproperlyConfigured

from maykin_common.config import ENVVAR_REGISTRY, config
from open_api_framework.conf.base import *  # noqa

from .api import *  # noqa

DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = config(
    "DB_DISABLE_SERVER_SIDE_CURSORS",
    default=False,
    documentation=DocumentationParams(
        help_text=(
            "Whether or not server side cursors should be disabled for Postgres connections. "
            "Setting this to true is required when using a connection pooler in "
            "transaction mode (like PgBouncer). "
            "**WARNING:** the effect of disabling server side cursors on performance has not "
            "been thoroughly tested yet."
        ),
        group="Database",
    ),
)

DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

# Application definition

INSTALLED_APPS = INSTALLED_APPS + [
    "maykin_common",
    "capture_tag",
    # Optional applications.
    "django.contrib.gis",
    # External applications.
    "rest_framework_gis",
    "jsonsuit.apps.JSONSuitConfig",
    # Project applications.
    "objects.accounts",
    "objects.setup_configuration",
    "objects.api",
    "objects.core",
    "objects.token",
    "objects.utils",
]

MIDDLEWARE += [
    "vng_api_common.middleware.APIVersionHeaderMiddleware",
]
# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

# FIXME should this be `nl-nl`?
LANGUAGE_CODE = "en-us"
# FIXME should this be UTC?
TIME_ZONE = "Europe/Amsterdam"

#
# Additional Django settings
#


#
# Custom settings
#
PROJECT_NAME = "Open Object"
SITE_TITLE = "Starting point"
SHOW_ALERT = True

# TODO remove this once https://github.com/maykinmedia/open-object/issues/621 is fixed
OBJECTS_ADMIN_SEARCH_DISABLED = config(
    "OBJECTS_ADMIN_SEARCH_DISABLED",
    documentation=DocumentationParams(
        help_text=(
            "Indicates whether or not searching in the Objects admin should be disabled"
        ),
    ),
    default=False,
)

# Default (connection timeout, read timeout) for the requests library (in seconds)
REQUESTS_DEFAULT_TIMEOUT = (10, 30)

#
# Library settings
#


# Django-Admin-Index
ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION = (
    "maykin_common.django_two_factor_auth.should_display_dropdown_menu"
)

#
# MAYKIN-2FA
#
# It uses django-two-factor-auth under the hood so you can configure
# those settings too.
#
# we run the admin site monkeypatch instead.
# Relying Party name for WebAuthn (hardware tokens)
TWO_FACTOR_WEBAUTHN_RP_NAME = "objects api"

# settings for sending notifications
NOTIFICATIONS_KANAAL = "objecten"

ENABLE_CLOUD_EVENTS = config(
    "ENABLE_CLOUD_EVENTS",
    default="False",
    cast=bool,
    documentation=DocumentationParams(
        help_text="**EXPERIMENTAL**: indicates whether or not cloud events should be sent to the configured endpoint for specific operations on Zaak (not ready for use in production)",
    ),
)

NOTIFICATIONS_SOURCE = config(
    "NOTIFICATIONS_SOURCE",
    default="",
    documentation=DocumentationParams(
        help_text="**EXPERIMENTAL**: the identifier of this application to use as the source in notifications and cloudevents",
    ),
)

if ENABLE_CLOUD_EVENTS and not NOTIFICATIONS_SOURCE:
    raise ImproperlyConfigured("NOTIFICATIONS_SOURCE is REQUIRED for CloudEvents")

#
# CELERY
#
# TODO: this is an override because `open-api-framework` incorrectly uses the
# `CELERY_RESULT_BACKEND` envvar for the `CELERY_BROKER_URL` setting. This should be
# moved to OAF once all projects have made this breaking change
CELERY_BROKER_URL = config(
    "CELERY_BROKER_URL",
    default="redis://localhost:6379/1",
    documentation=DocumentationParams(
        help_text="the URL of the broker that will be used by Celery to send the notifications",
        group="Celery",
    ),
)
CELERY_RESULT_EXPIRES = config(
    "CELERY_RESULT_EXPIRES",
    default=3600,
    documentation=DocumentationParams(
        help_text=(
            "How long the results of tasks will be stored in Redis (in seconds),"
            " this can be set to a lower duration to lower memory usage for Redis."
        ),
        group="Celery",
    ),
)

# Add (by default) 5 (soft), 15 (hard) minute timeouts to all Celery tasks.
CELERY_TASK_TIME_LIMIT = config(
    "CELERY_TASK_HARD_TIME_LIMIT",
    default=15 * 60,
    documentation=DocumentationParams(
        help_text=(
            "Defaults to: ``900`` seconds. "
            "If a celery task exceeds this time limit, the worker processing the task will "
            "be killed and replaced with a new one."
        ),
        group="Celery",
    ),
)  # hard

#
# Django setup configuration
#
SETUP_CONFIGURATION_STEPS = (
    "zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep",
    "notifications_api_common.contrib.setup_configuration.steps.NotificationConfigurationStep",
    "mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep",
    "objects.setup_configuration.steps.objecttypes.ObjectTypesConfigurationStep",
    "objects.setup_configuration.steps.token_auth.TokenAuthConfigurationStep",
)

NOTIFICATIONS_API_GET_DOMAIN = "objects.utils.get_domain"

#
# DJANGO-STRUCTLOG
#
DJANGO_STRUCTLOG_IP_LOGGING_ENABLED = False
DJANGO_STRUCTLOG_CELERY_ENABLED = True

#
# SECURITY settings
#
CSRF_FAILURE_VIEW = "maykin_common.views.csrf_failure"

# This setting is used by the csrf_failure view (accounts app).
# You can specify any path that should match the request.path
# Note: the LOGIN_URL Django setting is not used because you could have
# multiple login urls defined.
LOGIN_URLS = [reverse_lazy("admin:login")]


UPGRADE_CHECK_PATHS: UpgradePaths = {
    "4.0.0": UpgradeCheck(
        VersionRange(minimum="3.6.1"),
        code_checks=[CommandCheck("check_for_external_objecttypes")],
    ),
}

#
# DJANGO-LOG-OUTGOING-REQUESTS
#
# XXX: Overrides to bring envvars in line with Open Forms, this is currently defined in
# open-api-framework using `LOG_REQUESTS`
LOG_OUTGOING_REQUESTS = config(
    "LOG_OUTGOING_REQUESTS",
    default=False,
    documentation=DocumentationParams(
        help_text=(
            "enable logging of the outgoing requests. "
            "This must be enabled along with `LOG_OUTGOING_REQUESTS_DB_SAVE` to save outgoing request logs in the database."
        ),
        group="Logging",
    ),
)
LOGGING["loggers"]["log_outgoing_requests"]["handlers"] = (
    ["log_outgoing_requests", "save_outgoing_requests"] if LOG_OUTGOING_REQUESTS else []
)

#
# DJANGO-STRUCTLOG
#
# Make sure the old envvar no longer shows up in the documentation
ENVVAR_REGISTRY.pop("ENABLE_STRUCTLOG_REQUESTS", None)
# XXX: Overrides to bring envvars in line with Open Forms, this is currently defined in
# open-api-framework using `ENABLE_STRUCTLOG_REQUESTS`
LOG_REQUESTS = config(
    "LOG_REQUESTS",
    default=True,
    documentation=DocumentationParams(
        help_text=("enable structured logging of requests"),
        group="Logging",
    ),
)

LOGGING["loggers"]["django.server"]["level"] = "WARNING" if LOG_REQUESTS else "INFO"

# If the old envvar `ENABLE_STRUCTLOG_REQUESTS` was used, avoid duplicate middleware
if "django_structlog.middlewares.RequestMiddleware" in MIDDLEWARE:
    MIDDLEWARE.remove("django_structlog.middlewares.RequestMiddleware")

if LOG_REQUESTS:
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1,
        "django_structlog.middlewares.RequestMiddleware",
    )

#
# OPEN-API-FRAMEWORK
#
# Override because SITE_DOMAIN has become required in 4.0.0
SITE_DOMAIN = config(
    "SITE_DOMAIN",
    documentation=DocumentationParams(
        help_text=("Defines the primary domain where the application is hosted."),
    ),
)
