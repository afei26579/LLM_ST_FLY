import uuid
from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """为每个请求生成唯一ID"""
    
    def process_request(self, request):
        """在请求处理前生成request_id"""
        request.request_id = str(uuid.uuid4())
        return None
    
    def process_response(self, request, response):
        """在响应中添加request_id头"""
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        return response