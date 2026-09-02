import logging  # noqa: TID251, TID253 - correct use to replace stdlib logging
import os

from django.http import HttpResponse

logger = logging.getLogger(__name__)


class PyInstrumentMiddleware:  # pragma:no cover
    """
    Middleware that's included in dev environments if `USE_PYINSTRUMENT=true`,
    allows profiling of the request/response cycle. Profiling results can be viewed
    at `/_profiling`
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.profiler_output_path = "/tmp/pyinstrument_profile.html"

    def __call__(self, request):
        if request.path.startswith("/_profiling"):
            return self._serve_profile()

        # Local import to avoid having to install this in production environments
        from pyinstrument import Profiler  # type: ignore[reportMissingImports]

        profiler = Profiler()
        profiler.start()

        response = self.get_response(request)

        profiler.stop()

        # Save the profile to an HTML file
        with open(self.profiler_output_path, "w") as f:
            f.write(profiler.output_html())

        return response

    def _serve_profile(self):
        """Serve the latest profiling report"""
        if os.path.exists(self.profiler_output_path):
            with open(self.profiler_output_path, "r") as f:
                return HttpResponse(f.read(), content_type="text/html")
        return HttpResponse("No profiling report available yet.", status=404)
