from django.utils.deprecation import MiddlewareMixin

class UserLastLoginIPMiddleware(MiddlewareMixin):
    """
    中间件：记录用户最后登录IP
    """
    def process_request(self, request):
        """处理请求，获取用户IP并保存"""
        # 仅处理已认证用户
        if not request.user.is_authenticated:
            return None
        
        # 获取客户端IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # 如果通过代理，取第一个IP
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # 如果IP发生变化，则更新用户的last_login_ip字段
        if request.user.last_login_ip != ip:
            request.user.last_login_ip = ip
            request.user.save(update_fields=['last_login_ip'])
        
        return None 