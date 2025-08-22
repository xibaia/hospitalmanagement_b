#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活患者账户的脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospitalmanagement.settings')
django.setup()

from hospital.models import Patient
from django.contrib.auth.models import User

def activate_latest_patient():
    """激活最新注册的患者"""
    try:
        # 获取最新注册的患者
        latest_patient = Patient.objects.filter(status=False).order_by('-id').first()
        
        if latest_patient:
            # 激活患者
            latest_patient.status = True
            latest_patient.save()
            
            print(f"✅ 成功激活患者: {latest_patient.user.username} ({latest_patient.user.get_full_name()})")
            print(f"患者ID: {latest_patient.id}")
            print(f"用户ID: {latest_patient.user.id}")
            return True
        else:
            print("❌ 没有找到需要激活的患者")
            return False
            
    except Exception as e:
        print(f"❌ 激活患者时出错: {str(e)}")
        return False

def activate_all_patients():
    """激活所有未激活的患者"""
    try:
        inactive_patients = Patient.objects.filter(status=False)
        count = inactive_patients.count()
        
        if count > 0:
            # 批量激活
            inactive_patients.update(status=True)
            print(f"✅ 成功激活 {count} 位患者")
            
            # 显示激活的患者列表
            for patient in inactive_patients:
                print(f"  - {patient.user.username} ({patient.user.get_full_name()})")
            return True
        else:
            print("❌ 没有找到需要激活的患者")
            return False
            
    except Exception as e:
        print(f"❌ 激活患者时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("🏥 患者账户激活工具")
    print("="*40)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        print("激活所有未激活的患者...")
        success = activate_all_patients()
    else:
        print("激活最新注册的患者...")
        success = activate_latest_patient()
    
    if success:
        print("\n🎉 操作完成！")
    else:
        print("\n⚠️ 操作失败！")

if __name__ == "__main__":
    main()