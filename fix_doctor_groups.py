#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospitalmanagement.settings')
django.setup()

from django.contrib.auth.models import User, Group
from hospital.models import Doctor

def fix_doctor_groups():
    try:
        # 检查医生用户
        doctor_user = User.objects.get(username='doctor_zhang')
        print(f'医生用户: {doctor_user.username}')
        print(f'当前用户组: {[g.name for g in doctor_user.groups.all()]}')
        
        # 检查医生记录
        doctor = Doctor.objects.get(user=doctor_user)
        print(f'医生状态: {doctor.status}')
        
        # 确保DOCTOR组存在
        doctor_group, created = Group.objects.get_or_create(name='DOCTOR')
        if created:
            print('创建了DOCTOR组')
        else:
            print('DOCTOR组已存在')
        
        # 将医生用户添加到DOCTOR组
        if doctor_user not in doctor_group.user_set.all():
            doctor_group.user_set.add(doctor_user)
            print('✅ 已将医生用户添加到DOCTOR组')
        else:
            print('医生用户已在DOCTOR组中')
            
        # 再次检查用户组
        doctor_user.refresh_from_db()
        print(f'修复后用户组: {[g.name for g in doctor_user.groups.all()]}')
        
        # 检查患者用户
        try:
            patient_user = User.objects.get(username='patient_li')
            print(f'\n患者用户: {patient_user.username}')
            print(f'患者用户组: {[g.name for g in patient_user.groups.all()]}')
            
            # 确保PATIENT组存在并添加患者
            patient_group, created = Group.objects.get_or_create(name='PATIENT')
            if patient_user not in patient_group.user_set.all():
                patient_group.user_set.add(patient_user)
                print('✅ 已将患者用户添加到PATIENT组')
        except User.DoesNotExist:
            print('患者用户不存在')
            
    except User.DoesNotExist:
        print('❌ 医生用户 doctor_zhang 不存在')
    except Doctor.DoesNotExist:
        print('❌ 医生记录不存在')
    except Exception as e:
        print(f'❌ 错误: {e}')

if __name__ == '__main__':
    fix_doctor_groups()