"""
生产环境推荐的认证配置
"""

# 生产环境认证配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # JWT作为主要认证方式（推荐）
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # Token认证作为备用（用于某些特殊场景）
        'rest_framework.authentication.TokenAuthentication',
        # 会话认证（用于Web界面）
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # 其他配置保持不变...
}

# JWT配置（生产环境推荐）
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # 访问令牌1小时过期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # 刷新令牌7天过期
    'ROTATE_REFRESH_TOKENS': True,                    # 启用刷新令牌轮换
    'BLACKLIST_AFTER_ROTATION': True,                 # 轮换后将旧令牌加入黑名单
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Token认证的安全增强
TOKEN_AUTHENTICATION_SETTINGS = {
    'AUTO_REFRESH_TOKENS': True,                      # 自动刷新过期token
    'TOKEN_EXPIRE_DAYS': 30,                          # Token 30天过期
    'MAX_TOKENS_PER_USER': 5,                         # 每用户最多5个token
}