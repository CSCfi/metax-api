from environ import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)

from metax_api.settings import env
REMS = {
    "ENABLED": env("REMS_ENABLED"),
}
if REMS["ENABLED"]:
    try:
        REMS["API_KEY"]: env("REMS_API_KEY") # noqa: F821
        REMS["BASE_URL"]: env("REMS_BASE_URL") # noqa: F821
        REMS["ETSIN_URL_TEMPLATE"]: env("REMS_ETSIN_URL_TEMPLATE") # noqa: F821
        REMS["METAX_USER"]: env("REMS_METAX_USER") # noqa: F821
        REMS["REPORTER_USER"]: env("REMS_REPORTER_USER") # noqa: F821
        REMS["AUTO_APPROVER"]: env("REMS_AUTO_APPROVER") # noqa: F821
        REMS["FORM_ID"]: int(env("REMS_FORM_ID")) # noqa: F821
    except ImproperlyConfigured as e:
        logger.warning(e)