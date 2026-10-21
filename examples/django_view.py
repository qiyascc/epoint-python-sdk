from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from epoint_sdk import Epoint, SignatureError

epoint = Epoint()


@csrf_exempt
@require_POST
def epoint_callback(request):
    try:
        tx = epoint.verify_callback(request.POST)
    except SignatureError:
        return HttpResponseBadRequest()
    if tx.paid:
        mark_paid(tx.order_id, tx.amount, tx.transaction)
    return HttpResponse("OK")


def mark_paid(order_id, amount, transaction):
    raise NotImplementedError
