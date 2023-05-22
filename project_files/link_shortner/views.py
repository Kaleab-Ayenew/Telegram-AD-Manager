from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.http import HttpResponseRedirect

from .models import ShortLink


@api_view(['GET'])
@permission_classes((AllowAny,))
def go_to_link(request, link_id):
    link_filter = ShortLink.objects.filter(link_id=link_id)
    if link_filter.exists():
        long_link = link_filter.first().long_link
        return HttpResponseRedirect(redirect_to=long_link)
    else:
        return Response(data="Invalid Link", status=status.HTTP_404_NOT_FOUND)
