#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医院管理系统API接口可用性测试脚本
"""

import requests
import json
import sys
from datetime import datetime

# API基础配置
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

# 测试数据 - 使用固定用户名进行测试
TEST_USER_DATA = {
    "first_name": "测试",
    "last_name": "用户",
    "username": "testuser_20250720_104535",  # 使用已激活的用户
    "password": "password123",
    "confirm_password": "password123",
    "address": "北京市朝阳区测试地址",
    "mobile": "13800138000",
    "symptoms": "测试症状",
    "assigned_doctor_id": None
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.patient_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if response_data:
            result["response_data"] = response_data
        self.test_results.append(result)
        
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status} - {test_name}: {message}")
        
    def test_server_connection(self):
        """测试服务器连接"""
        try:
            response = self.session.get(BASE_URL, timeout=5)
            if response.status_code == 200:
                self.log_test("服务器连接", True, "服务器运行正常")
                return True
            else:
                self.log_test("服务器连接", False, f"服务器响应异常: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("服务器连接", False, f"连接失败: {str(e)}")
            return False
            
    def test_patient_register(self):
        """测试患者注册接口"""
        try:
            url = f"{API_BASE}/patient/register/"
            response = self.session.post(url, json=TEST_USER_DATA, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                self.patient_id = data.get('patient_id')
                self.log_test("患者注册", True, f"注册成功，患者ID: {self.patient_id}", data)
                return True
            else:
                error_msg = response.text
                self.log_test("患者注册", False, f"注册失败 ({response.status_code}): {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("患者注册", False, f"请求异常: {str(e)}")
            return False
            
    def test_patient_login(self):
        """测试患者登录接口"""
        try:
            url = f"{API_BASE}/patient/login/"
            login_data = {
                "username": TEST_USER_DATA["username"],
                "password": TEST_USER_DATA["password"]
            }
            response = self.session.post(url, json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('data', {}).get('token')
                    if self.token:
                        self.log_test("患者登录", True, f"登录成功，获取Token: {self.token[:20]}...", data)
                        return True
                    else:
                        self.log_test("患者登录", False, "登录响应中缺少Token", data)
                        return False
                else:
                    self.log_test("患者登录", False, f"登录失败: {data.get('message', '未知错误')}", data)
                    return False
            else:
                error_msg = response.text
                self.log_test("患者登录", False, f"登录失败 ({response.status_code}): {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("患者登录", False, f"请求异常: {str(e)}")
            return False
            
    def test_patient_info(self):
        """测试获取患者信息接口"""
        if not self.token:
            self.log_test("获取患者信息", False, "缺少认证Token")
            return False
            
        try:
            url = f"{API_BASE}/patient/info/"
            headers = {"Authorization": f"Token {self.token}"}
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("获取患者信息", True, "成功获取患者信息", data)
                return True
            else:
                error_msg = response.text
                self.log_test("获取患者信息", False, f"获取失败 ({response.status_code}): {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("获取患者信息", False, f"请求异常: {str(e)}")
            return False
            
    def test_update_patient_info(self):
        """测试更新患者信息接口"""
        if not self.token:
            self.log_test("更新患者信息", False, "缺少认证Token")
            return False
            
        try:
            url = f"{API_BASE}/patient/update/"
            headers = {"Authorization": f"Token {self.token}"}
            update_data = {
                "address": "上海市浦东新区更新地址",
                "symptoms": "更新后的症状描述"
            }
            response = self.session.put(url, json=update_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("更新患者信息", True, "患者信息更新成功", data)
                return True
            else:
                error_msg = response.text
                self.log_test("更新患者信息", False, f"更新失败 ({response.status_code}): {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("更新患者信息", False, f"请求异常: {str(e)}")
            return False
            
    def test_doctors_list(self):
        """测试获取医生列表接口"""
        try:
            url = f"{API_BASE}/doctors/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # 修正医生数量计算逻辑
                if isinstance(data, dict) and 'data' in data:
                    doctor_list = data['data']
                    doctor_count = len(doctor_list) if isinstance(doctor_list, list) else 0
                elif isinstance(data, list):
                    doctor_count = len(data)
                else:
                    doctor_count = 0
                self.log_test("获取医生列表", True, f"成功获取医生列表，共{doctor_count}位医生", data)
                return True
            else:
                error_msg = response.text
                self.log_test("获取医生列表", False, f"获取失败 ({response.status_code}): {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("获取医生列表", False, f"请求异常: {str(e)}")
            return False
            
    def test_patient_logout(self):
        """测试患者登出接口"""
        if not self.token:
            self.log_test("患者登出", False, "缺少认证Token")
            return False
            
        try:
            url = f"{API_BASE}/patient/logout/"
            headers = {"Authorization": f"Token {self.token}"}
            response = self.session.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("患者登出", True, "登出成功", data)
                return True
            else:
                error_msg = response.text
                self.log_test("患者登出", False, f"登出失败 ({response.status_code}): {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("患者登出", False, f"请求异常: {str(e)}")
            return False
            
    def run_all_tests(self):
        """运行所有测试"""
        print("="*60)
        print("🏥 医院管理系统API接口可用性测试")
        print("="*60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"服务器地址: {BASE_URL}")
        print(f"测试用户: {TEST_USER_DATA['username']}")
        print("-"*60)
        
        # 按顺序执行测试
        tests = [
            ("服务器连接测试", self.test_server_connection),
            ("医生列表接口测试", self.test_doctors_list),
            ("患者登录接口测试", self.test_patient_login),
            ("获取患者信息接口测试", self.test_patient_info),
            ("更新患者信息接口测试", self.test_update_patient_info),
            ("患者登出接口测试", self.test_patient_logout),
        ]
        
        for test_desc, test_func in tests:
            print(f"\n🔍 {test_desc}")
            test_func()
            
        # 生成测试报告
        return self.generate_report()
        
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 测试报告")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        # 保存详细报告到文件
        report_file = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": f"{(passed_tests/total_tests*100):.1f}%"
                },
                "test_results": self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return passed_tests == total_tests

def main():
    """主函数"""
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有API接口测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️  部分API接口测试失败，请检查服务器状态和接口实现。")
        sys.exit(1)

if __name__ == "__main__":
    main()