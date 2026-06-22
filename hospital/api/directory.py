from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from hospital.api.common import paginated_response
from hospital.models import Doctor
from hospital.serializers import DoctorListSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def doctors_list_api(request):
    doctors = Doctor.objects.filter(status=True).order_by('id')
    return paginated_response(request, doctors, DoctorListSerializer, message='获取成功')
