"""
响应格式验证工具
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class ResponseValidator:
    """响应格式验证器"""
    
    @staticmethod
    def validate_response_format(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证响应格式是否符合标准
        
        Args:
            response_data: 响应数据字典
            
        Returns:
            验证结果字典，包含is_valid和errors字段
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['code', 'message', 'data', 'timestamp', 'request_id']
        for field in required_fields:
            if field not in response_data:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查字段类型
        if 'code' in response_data:
            if not isinstance(response_data['code'], int):
                errors.append("code字段必须是整数类型")
            elif response_data['code'] not in [200, 400, 401, 403, 404, 500]:
                errors.append(f"code字段值无效: {response_data['code']}")
        
        if 'message' in response_data:
            if not isinstance(response_data['message'], str):
                errors.append("message字段必须是字符串类型")
        
        if 'timestamp' in response_data:
            if not isinstance(response_data['timestamp'], str):
                errors.append("timestamp字段必须是字符串类型")
            else:
                try:
                    datetime.fromisoformat(response_data['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    errors.append("timestamp字段格式无效，应为ISO格式")
        
        if 'request_id' in response_data:
            if not isinstance(response_data['request_id'], str):
                errors.append("request_id字段必须是字符串类型")
            else:
                try:
                    uuid.UUID(response_data['request_id'])
                except ValueError:
                    # 允许非UUID格式的request_id（如测试用的字符串）
                    pass
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_paginated_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证分页响应格式
        
        Args:
            response_data: 响应数据字典
            
        Returns:
            验证结果字典
        """
        # 先验证基本格式
        result = ResponseValidator.validate_response_format(response_data)
        
        if not result['is_valid']:
            return result
        
        # 检查分页特有字段
        data = response_data.get('data', {})
        if not isinstance(data, dict):
            result['errors'].append("分页响应的data字段必须是字典类型")
            result['is_valid'] = False
            return result
        
        required_pagination_fields = ['list', 'total']
        for field in required_pagination_fields:
            if field not in data:
                result['errors'].append(f"分页响应缺少必需字段: data.{field}")
        
        if 'list' in data and not isinstance(data['list'], list):
            result['errors'].append("data.list字段必须是数组类型")
        
        if 'total' in data and not isinstance(data['total'], int):
            result['errors'].append("data.total字段必须是整数类型")
        
        result['is_valid'] = len(result['errors']) == 0
        return result


class ResponseHelper:
    """响应格式辅助工具"""
    
    @staticmethod
    def extract_error_info(response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        从响应中提取错误信息
        
        Args:
            response_data: 响应数据字典
            
        Returns:
            错误信息字典或None
        """
        if response_data.get('code') != 200:
            return {
                'code': response_data.get('code'),
                'message': response_data.get('message'),
                'data': response_data.get('data'),
                'request_id': response_data.get('request_id')
            }
        return None
    
    @staticmethod
    def is_success_response(response_data: Dict[str, Any]) -> bool:
        """
        判断响应是否成功
        
        Args:
            response_data: 响应数据字典
            
        Returns:
            是否成功
        """
        return response_data.get('code') == 200
    
    @staticmethod
    def get_response_data(response_data: Dict[str, Any]) -> Any:
        """
        获取响应中的数据部分
        
        Args:
            response_data: 响应数据字典
            
        Returns:
            数据部分
        """
        return response_data.get('data')
    
    @staticmethod
    def format_error_message(error_code: int, error_message: str, request_id: str = None) -> str:
        """
        格式化错误消息
        
        Args:
            error_code: 错误码
            error_message: 错误消息
            request_id: 请求ID
            
        Returns:
            格式化后的错误消息
        """
        base_message = f"[{error_code}] {error_message}"
        if request_id:
            base_message += f" (请求ID: {request_id})"
        return base_message