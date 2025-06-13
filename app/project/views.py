import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


logger = logging.getLogger("app")


def health_check(request):
    return HttpResponse("success", status=200)


@login_required()
@require_http_methods(["POST"])
def flush_cache_view(request):
    logger.debug("flush_cache_view")
    # flush_template_cache.delay()
    messages.success(request, "Cache flush success.")
    return HttpResponse(status=204)


def handler400_view(request, exception):
    logger.debug("handler400_view")
    logger.debug(exception)
    return render(request, "error/400.html", status=400)


def handler403_view(request, exception):
    logger.debug("handler403_view")
    logger.debug(exception)
    return render(request, "error/403.html", status=403)


def handler404_view(request, exception):
    logger.debug("handler404_view")
    logger.debug(exception)
    return render(request, "error/404.html", status=404)


def handler500_view(request):
    logger.debug("handler500_view")
    return render(request, "error/500.html", status=500)


def dal_view(request):
    """
    View  /.well-known/assetlinks.json
    """
    assetlinks = [
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": "org.cssnr.tibs3dprints",
                "sha256_cert_fingerprints": [
                    # Play
                    "A0:C3:AE:E3:53:BE:63:E5:5A:A5:37:B2:87:21:78:A7:EC:6C:72:BA:54:78:05:96:30:EE:AF:EB:FB:1B:95:A0",
                    # Release
                    "37:A8:52:C1:51:BD:F3:2E:B7:2C:EF:2F:4F:6B:A2:AA:2B:59:8A:37:49:C3:CE:F4:ED:A0:77:23:73:59:C7:11",
                    # Developer Debug
                    "6E:F0:94:D9:F6:E2:65:1A:FC:FB:2F:1A:7F:8A:64:C8:A6:6D:6F:37:29:6C:C5:F7:D4:97:CD:8C:64:42:D5:D9",
                ],
            },
        }
    ]
    return JsonResponse(assetlinks, safe=False)
