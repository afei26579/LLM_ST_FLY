"""
测试专用的Django设置
使用SQLite内存数据库，避免权限问题
"""

from .settings import *

# 使用SQLite内存数据库进行测试
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 禁用迁移以加快测试速度
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# 简化密码验证以加快测试
AUTH_PASSWORD_VALIDATORS = []

# 禁用日志输出
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# 禁用缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 测试时不需要真实的API密钥
DASHSCOPE_API_KEY = 'test_api_key'

# 禁用CSRF保护
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# 简化中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]