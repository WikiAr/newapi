import pytest
import sys
import os

# إضافة مسار المشروع إلى sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def api_credentials():
    """بيانات اعتماد مشتركة للاختبارات"""
    from newapi import useraccount
    return {
        "username": useraccount.username,
        "password": useraccount.password
    }

@pytest.fixture
def temp_test_page():
    """صفحة اختبار مؤقتة"""
    return "User:TestBot/pytest_sandbox"
