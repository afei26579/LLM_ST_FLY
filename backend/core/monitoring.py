"""
响应格式监控工具
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from .validators import ResponseValidator

logger = logging.getLogger(__name__)


class ResponseMonitor:
    """响应格式监控器"""
    
    CACHE_PREFIX = 'response_monitor'
    CACHE_TIMEOUT = 3600  # 1小时
    
    @classmethod
    def record_response(cls, response_data: Dict[str, Any], endpoint: str = None, 
                       user_id: int = None, duration: float = None):
        """
        记录响应信息
        
        Args:
            response_data: 响应数据
            endpoint: API端点
            user_id: 用户ID
            duration: 响应时间（毫秒）
        """
        try:
            # 验证响应格式
            validation_result = ResponseValidator.validate_response_format(response_data)
            
            # 记录统计信息
            stats_key = f"{cls.CACHE_PREFIX}:stats"
            stats = cache.get(stats_key, {
                'total_responses': 0,
                'success_responses': 0,
                'error_responses': 0,
                'format_errors': 0,
                'avg_response_time': 0,
                'endpoints': {},
                'error_codes': {},
                'last_updated': datetime.now().isoformat()
            })
            
            # 更新统计
            stats['total_responses'] += 1
            
            if validation_result['is_valid']:
                if response_data.get('code') == 200:
                    stats['success_responses'] += 1
                else:
                    stats['error_responses'] += 1
                    error_code = response_data.get('code', 'unknown')
                    stats['error_codes'][str(error_code)] = stats['error_codes'].get(str(error_code), 0) + 1
            else:
                stats['format_errors'] += 1
                logger.warning(f"响应格式验证失败: {validation_result['errors']}")
            
            # 记录端点统计
            if endpoint:
                if endpoint not in stats['endpoints']:
                    stats['endpoints'][endpoint] = {
                        'count': 0,
                        'success': 0,
                        'error': 0,
                        'avg_time': 0
                    }
                
                endpoint_stats = stats['endpoints'][endpoint]
                endpoint_stats['count'] += 1
                
                if response_data.get('code') == 200:
                    endpoint_stats['success'] += 1
                else:
                    endpoint_stats['error'] += 1
                
                if duration is not None:
                    # 计算平均响应时间
                    current_avg = endpoint_stats['avg_time']
                    count = endpoint_stats['count']
                    endpoint_stats['avg_time'] = (current_avg * (count - 1) + duration) / count
            
            # 更新全局平均响应时间
            if duration is not None:
                current_avg = stats['avg_response_time']
                total = stats['total_responses']
                stats['avg_response_time'] = (current_avg * (total - 1) + duration) / total
            
            stats['last_updated'] = datetime.now().isoformat()
            cache.set(stats_key, stats, cls.CACHE_TIMEOUT)
            
        except Exception as e:
            logger.error(f"记录响应监控信息失败: {str(e)}")
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        获取监控统计信息
        
        Returns:
            统计信息字典
        """
        stats_key = f"{cls.CACHE_PREFIX}:stats"
        return cache.get(stats_key, {
            'total_responses': 0,
            'success_responses': 0,
            'error_responses': 0,
            'format_errors': 0,
            'avg_response_time': 0,
            'endpoints': {},
            'error_codes': {},
            'last_updated': None
        })
    
    @classmethod
    def get_health_status(cls) -> Dict[str, Any]:
        """
        获取系统健康状态
        
        Returns:
            健康状态信息
        """
        stats = cls.get_stats()
        total = stats['total_responses']
        
        if total == 0:
            return {
                'status': 'unknown',
                'message': '暂无响应数据',
                'success_rate': 0,
                'error_rate': 0,
                'format_error_rate': 0
            }
        
        success_rate = (stats['success_responses'] / total) * 100
        error_rate = (stats['error_responses'] / total) * 100
        format_error_rate = (stats['format_errors'] / total) * 100
        
        # 判断健康状态
        if success_rate >= 95 and format_error_rate < 1:
            status = 'healthy'
            message = '系统运行正常'
        elif success_rate >= 90 and format_error_rate < 5:
            status = 'warning'
            message = '系统运行基本正常，需要关注'
        else:
            status = 'critical'
            message = '系统存在问题，需要立即处理'
        
        return {
            'status': status,
            'message': message,
            'success_rate': round(success_rate, 2),
            'error_rate': round(error_rate, 2),
            'format_error_rate': round(format_error_rate, 2),
            'avg_response_time': round(stats['avg_response_time'], 2),
            'total_responses': total,
            'last_updated': stats['last_updated']
        }
    
    @classmethod
    def reset_stats(cls):
        """重置统计信息"""
        stats_key = f"{cls.CACHE_PREFIX}:stats"
        cache.delete(stats_key)
        logger.info("响应监控统计信息已重置")


class ResponseMiddleware:
    """响应监控中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = datetime.now()
        
        response = self.get_response(request)
        
        # 计算响应时间
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        # 只监控API响应
        if request.path.startswith('/api/'):
            try:
                # 尝试解析响应数据
                if hasattr(response, 'data') and isinstance(response.data, dict):
                    ResponseMonitor.record_response(
                        response_data=response.data,
                        endpoint=request.path,
                        user_id=getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                        duration=duration
                    )
            except Exception as e:
                logger.error(f"响应监控中间件处理失败: {str(e)}")
        
        return response