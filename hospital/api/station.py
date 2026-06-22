from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from hospital.api.common import paginated_response
from hospital.models import Station
from hospital.serializers import StationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stations_list_api(request):
    stations = Station.objects.filter(is_active=True).order_by('name')
    return paginated_response(request, stations, StationSerializer)
