# pragma: no cover
import os
import sys
import warnings

os.environ.setdefault("DEBUG", "yes")
os.environ.setdefault("ALLOWED_HOSTS", "*")
os.environ.setdefault(
    "SECRET_KEY", "2(@f(-6s_u(5fd&1sg^uvu2s(c-9sapw)1era8q&)g)h@cwxxg"
)
os.environ.setdefault("SITE_DOMAIN", "localhost:8000")
os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("RELEASE", "dev")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DISABLE_2FA", "True")
os.environ.setdefault("LOG_FORMAT_CONSOLE", "plain_console")

os.environ.setdefault("DB_NAME", "objects")
os.environ.setdefault("DB_USER", "objects")
os.environ.setdefault("DB_PASSWORD", "objects")

os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("OTEL_EXPORTER_OTLP_METRICS_INSECURE", "true")

from .base import *  # noqa isort:skip

#
# Standard Django settings.
#


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING["loggers"].update(
    {
        "objects": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["json_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "performance": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        #
        # See: https://code.djangoproject.com/ticket/30554
        # Autoreload logs excessively, turn it down a bit.
        #
        "django.utils.autoreload": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    }
)


#
# Library settings
#

# Django extensions
INSTALLED_APPS += ["django_extensions"]

ELASTIC_APM["DEBUG"] = True

# Django debug toolbar
INSTALLED_APPS += [
    "debug_toolbar",
]
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
INTERNAL_IPS = ("127.0.0.1",)
DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}

AXES_BEHIND_REVERSE_PROXY = (
    False  # Default: False (we are typically using Nginx as reverse proxy)
)

# in memory cache and django-axes don't get along.
# https://django-axes.readthedocs.io/en/latest/configuration.html#known-configuration-problems
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "axes_cache": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "oidc": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

AXES_CACHE = "axes_cache"


# THOU SHALT NOT USE NAIVE DATETIMES
warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)

#
# DJANGO-SILK
#
if config("PROFILE", default=False, add_to_docs=False):
    INSTALLED_APPS += ["silk"]
    MIDDLEWARE = ["silk.middleware.SilkyMiddleware"] + MIDDLEWARE
    security_index = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(security_index + 1, "whitenoise.middleware.WhiteNoiseMiddleware")


if config("USE_PYINSTRUMENT", default=False, add_to_docs=False):  # pragma:no cover
    MIDDLEWARE = ["objects.utils.middleware.PyInstrumentMiddleware"] + MIDDLEWARE


NOTIFICATIONS_DISABLED = config(
    "NOTIFICATIONS_DISABLED", default="test" in sys.argv, add_to_docs=False
)

# Override settings with local settings.
try:  # noqa: SIM105
    from .local import *  # noqa
except ImportError:
    pass
