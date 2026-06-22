from .activity import (
    activities_list_api,
    activity_detail_api,
    activity_join_api,
    activity_leave_api,
    my_activities_api,
)
from .directory import doctors_list_api
from .doctor import (
    doctor_login_api,
    doctor_logout_api,
    doctor_patients_api,
    doctor_patient_detail_api,
)
from .medical_record import (
    doctor_confirm_record_api,
    doctor_record_detail_api,
    doctor_records_api,
    patient_record_detail_api,
    patient_records_api,
)
from .patient import (
    bind_doctor_api,
    patient_info_api,
    patient_login_api,
    patient_logout_api,
    patient_medical_history_api,
    patient_register_api,
    update_patient_info_api,
)
from .station import stations_list_api
