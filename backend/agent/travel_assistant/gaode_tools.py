"""
高德地图工具集成
"""

import os
import logging
import httpx
from typing import Dict, Any, List, Optional
from langchain.tools import tool

logger = logging.getLogger(__name__)

# 高德地图 API Key
GD_API_KEY = os.getenv('GD_API_KEY', '')
BASE_URL = "https://restapi.amap.com/v3"


class GaodeMapError(Exception):
    """高德地图 API 错误"""
    pass


@tool
def search_poi(city: str, keywords: str, page_size: int = 10) -> str:
    """
    搜索 POI（兴趣点），如景点、餐厅、酒店等
    
    Args:
        city: 城市名称，如"北京"、"上海"
        keywords: 搜索关键词，如"景点"、"美食"、"酒店"
        page_size: 返回结果数量，默认10条
        
    Returns:
        JSON格式的POI列表字符串
    """
    if not GD_API_KEY:
        return "错误: 未配置高德地图 API Key"
    
    try:
        url = f"{BASE_URL}/place/text"
        params = {
            'key': GD_API_KEY,
            'keywords': keywords,
            'city': city,
            'offset': page_size,
            'page': 1,
            'extensions': 'all'
        }
        
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == '1' and data.get('pois'):
            pois = data['pois']
            results = []
            for poi in pois[:page_size]:
                results.append({
                    'name': poi.get('name', ''),
                    'type': poi.get('type', ''),
                    'address': poi.get('address', ''),
                    'location': poi.get('location', ''),
                    'tel': poi.get('tel', ''),
                    'rating': poi.get('biz_ext', {}).get('rating', ''),
                    'cost': poi.get('biz_ext', {}).get('cost', '')
                })
            
            import json
            return json.dumps(results, ensure_ascii=False, indent=2)
        else:
            return f"未找到相关POI: {keywords}"
            
    except Exception as e:
        logger.error(f"POI搜索失败: {e}")
        return f"POI搜索失败: {str(e)}"


@tool
def calculate_route(origin_city: str, origin_poi: str, dest_city: str, dest_poi: str, mode: str = "driving") -> str:
    """
    计算两个地点之间的路线和距离
    
    Args:
        origin_city: 起点城市
        origin_poi: 起点POI名称或地址
        dest_city: 终点城市
        dest_poi: 终点POI名称或地址
        mode: 出行方式 - driving(驾车), walking(步行), transit(公交)
        
    Returns:
        路线规划详情JSON字符串
    """
    if not GD_API_KEY:
        return "错误: 未配置高德地图 API Key"
    
    try:
        # 1. 先获取起点和终点的坐标
        origin_location = _get_poi_location(origin_city, origin_poi)
        dest_location = _get_poi_location(dest_city, dest_poi)
        
        if not origin_location or not dest_location:
            return "无法获取起点或终点坐标"
        
        # 2. 计算路线
        if mode == "driving":
            url = f"{BASE_URL}/direction/driving"
        elif mode == "walking":
            url = f"{BASE_URL}/direction/walking"
        elif mode == "transit":
            url = f"{BASE_URL}/direction/transit/integrated"
        else:
            return f"不支持的出行方式: {mode}"
        
        params = {
            'key': GD_API_KEY,
            'origin': origin_location,
            'destination': dest_location,
            'extensions': 'all'
        }
        
        if mode == "transit":
            params['city'] = dest_city
        
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == '1':
            route_info = _parse_route_response(data, mode)
            import json
            return json.dumps(route_info, ensure_ascii=False, indent=2)
        else:
            return f"路线规划失败: {data.get('info', '未知错误')}"
            
    except Exception as e:
        logger.error(f"路线规划失败: {e}")
        return f"路线规划失败: {str(e)}"


@tool
def get_weather(city: str) -> str:
    """
    查询城市天气信息
    
    Args:
        city: 城市名称或城市编码
        
    Returns:
        天气信息JSON字符串
    """
    if not GD_API_KEY:
        return "错误: 未配置高德地图 API Key"
    
    try:
        url = f"{BASE_URL}/weather/weatherInfo"
        params = {
            'key': GD_API_KEY,
            'city': city,
            'extensions': 'all'  # 获取未来天气预报
        }
        
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == '1' and data.get('forecasts'):
            forecast = data['forecasts'][0]
            result = {
                'city': forecast.get('city', ''),
                'province': forecast.get('province', ''),
                'report_time': forecast.get('reporttime', ''),
                'casts': []
            }
            
            for cast in forecast.get('casts', [])[:4]:  # 未来4天天气
                result['casts'].append({
                    'date': cast.get('date', ''),
                    'week': cast.get('week', ''),
                    'dayweather': cast.get('dayweather', ''),
                    'nightweather': cast.get('nightweather', ''),
                    'daytemp': cast.get('daytemp', ''),
                    'nighttemp': cast.get('nighttemp', ''),
                    'daywind': cast.get('daywind', ''),
                    'nightwind': cast.get('nightwind', '')
                })
            
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return f"获取天气失败: {data.get('info', '未知错误')}"
            
    except Exception as e:
        logger.error(f"天气查询失败: {e}")
        return f"天气查询失败: {str(e)}"


@tool
def geocode_address(city: str, address: str) -> str:
    """
    地理编码：将地址转换为经纬度坐标
    
    Args:
        city: 城市名称
        address: 详细地址
        
    Returns:
        坐标信息JSON字符串
    """
    if not GD_API_KEY:
        return "错误: 未配置高德地图 API Key"
    
    try:
        url = f"{BASE_URL}/geocode/geo"
        params = {
            'key': GD_API_KEY,
            'address': address,
            'city': city
        }
        
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == '1' and data.get('geocodes'):
            geocode = data['geocodes'][0]
            result = {
                'formatted_address': geocode.get('formatted_address', ''),
                'province': geocode.get('province', ''),
                'city': geocode.get('city', ''),
                'district': geocode.get('district', ''),
                'location': geocode.get('location', ''),
                'level': geocode.get('level', '')
            }
            
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return f"地理编码失败: {data.get('info', '未知错误')}"
            
    except Exception as e:
        logger.error(f"地理编码失败: {e}")
        return f"地理编码失败: {str(e)}"


# 辅助函数
def _get_poi_location(city: str, poi_name: str) -> Optional[str]:
    """获取POI的经纬度坐标"""
    try:
        url = f"{BASE_URL}/place/text"
        params = {
            'key': GD_API_KEY,
            'keywords': poi_name,
            'city': city,
            'offset': 1
        }
        
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == '1' and data.get('pois'):
            return data['pois'][0].get('location', '')
        return None
        
    except Exception as e:
        logger.error(f"获取POI坐标失败: {e}")
        return None


def _parse_route_response(data: Dict, mode: str) -> Dict[str, Any]:
    """解析路线响应数据"""
    result = {
        'mode': mode,
        'routes': []
    }
    
    try:
        if mode == "driving":
            route = data.get('route', {})
            paths = route.get('paths', [])
            if paths:
                path = paths[0]
                result['routes'].append({
                    'distance': path.get('distance', ''),  # 米
                    'duration': path.get('duration', ''),  # 秒
                    'strategy': path.get('strategy', ''),
                    'tolls': path.get('tolls', ''),  # 过路费
                    'toll_distance': path.get('toll_distance', ''),
                    'traffic_lights': path.get('traffic_lights', ''),
                    'steps': _extract_steps(path.get('steps', []))
                })
                
        elif mode == "walking":
            route = data.get('route', {})
            paths = route.get('paths', [])
            if paths:
                path = paths[0]
                result['routes'].append({
                    'distance': path.get('distance', ''),
                    'duration': path.get('duration', ''),
                    'steps': _extract_steps(path.get('steps', []))
                })
                
        elif mode == "transit":
            route = data.get('route', {})
            transits = route.get('transits', [])
            if transits:
                transit = transits[0]
                result['routes'].append({
                    'distance': transit.get('distance', ''),
                    'duration': transit.get('duration', ''),
                    'walking_distance': transit.get('walking_distance', ''),
                    'cost': transit.get('cost', ''),
                    'segments': _extract_transit_segments(transit.get('segments', []))
                })
    
    except Exception as e:
        logger.error(f"解析路线数据失败: {e}")
    
    return result


def _extract_steps(steps: List[Dict]) -> List[Dict]:
    """提取路径步骤"""
    result = []
    for step in steps[:5]:  # 只返回前5步
        result.append({
            'instruction': step.get('instruction', ''),
            'distance': step.get('distance', ''),
            'duration': step.get('duration', ''),
            'road': step.get('road', '')
        })
    return result


def _extract_transit_segments(segments: List[Dict]) -> List[Dict]:
    """提取公交换乘段落"""
    result = []
    for segment in segments[:5]:
        if segment.get('bus'):
            buslines = segment['bus'].get('buslines', [])
            if buslines:
                busline = buslines[0]
                result.append({
                    'type': 'bus',
                    'name': busline.get('name', ''),
                    'departure_stop': busline.get('departure_stop', {}).get('name', ''),
                    'arrival_stop': busline.get('arrival_stop', {}).get('name', ''),
                    'distance': busline.get('distance', ''),
                    'duration': busline.get('duration', '')
                })
        elif segment.get('walking'):
            walking = segment['walking']
            result.append({
                'type': 'walking',
                'distance': walking.get('distance', ''),
                'duration': walking.get('duration', '')
            })
    return result


# 导出所有工具
GAODE_TOOLS = [
    search_poi,
    calculate_route,
    get_weather,
    geocode_address
]

