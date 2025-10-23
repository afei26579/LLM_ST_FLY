/**
 * 高德地图 Hook
 * 封装高德地图SDK的初始化和操作
 */

import { ref, onMounted, onUnmounted } from 'vue'
import type { Ref } from 'vue'

// 高德地图API配置
const GD_API_KEY = import.meta.env.VITE_GD_API_KEY || ''

const GD_MAP_SDK_URL = `https://webapi.amap.com/maps?v=2.0&key=${GD_API_KEY}&v=20251021`

// 声明全局AMap类型
declare global {
  interface Window {
    AMap: any
    _AMapSecurityConfig?: {
      securityJsCode: string
    }
  }
}

// POI类型
interface POI {
  id: string
  name: string
  address: string
  location: {
    lng: number
    lat: number
  }
  type?: string
  tel?: string
}

// 标记类型
interface Marker {
  id: string
  position: [number, number]
  title: string
  content?: string
  poi?: POI
}

export function useGDMap(containerId: Ref<string>) {
  // 状态
  const map = ref<any>(null)
  const AMap = ref<any>(null)
  const isMapReady = ref(false)
  const markers = ref<any[]>([])
  const currentInfoWindow = ref<any>(null)

  /**
   * 加载高德地图SDK
   */
  const loadMapScript = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      // 检查是否已加载
      if (window.AMap) {
        AMap.value = window.AMap
        resolve()
        return
      }

      // 安全密钥配置（可选）
      const securityCode = import.meta.env.VITE_GD_SECURITY_CODE
      if (securityCode) {
        window._AMapSecurityConfig = {
          securityJsCode: securityCode
        }
      }

      // 创建script标签
      const script = document.createElement('script')
      script.src = GD_MAP_SDK_URL
      script.async = true
      script.onload = () => {
        AMap.value = window.AMap
        resolve()
      }
      script.onerror = reject
      document.head.appendChild(script)
    })
  }

  /**
   * 初始化地图
   */
  const initMap = async (options?: {
    center?: [number, number]
    zoom?: number
    city?: string
  }) => {
    try {
      await loadMapScript()

      if (!AMap.value) {
        throw new Error('高德地图SDK加载失败')
      }

      // 创建地图实例
      map.value = new AMap.value.Map(containerId.value, {
        zoom: options?.zoom || 12,
        center: options?.center || [116.397428, 39.90923], // 默认北京
        viewMode: '2D',
        resizeEnable: true
      })

      // 如果指定了城市，设置城市
      if (options?.city) {
        map.value.setCity(options.city)
      }

      isMapReady.value = true
      console.log('地图初始化成功')
    } catch (error) {
      console.error('地图初始化失败:', error)
      throw error
    }
  }

  /**
   * 添加标记
   */
  const addMarker = (markerData: Marker) => {
    if (!map.value || !AMap.value) {
      console.warn('地图未初始化')
      return null
    }

    const marker = new AMap.value.Marker({
      position: markerData.position,
      title: markerData.title,
      map: map.value,
      extData: {
        id: markerData.id,
        poi: markerData.poi
      }
    })

    // 添加点击事件
    marker.on('click', () => {
      showInfoWindow(marker, markerData)
    })

    markers.value.push(marker)
    return marker
  }

  /**
   * 批量添加标记
   */
  const addMarkers = (markerDataList: Marker[]) => {
    const addedMarkers = markerDataList.map(data => addMarker(data)).filter(m => m !== null)
    
    // 自动调整视野以包含所有标记
    if (addedMarkers.length > 0) {
      map.value.setFitView()
    }

    return addedMarkers
  }

  /**
   * 清除所有标记
   */
  const clearMarkers = () => {
    if (markers.value.length > 0) {
      map.value.remove(markers.value)
      markers.value = []
    }
    if (currentInfoWindow.value) {
      currentInfoWindow.value.close()
      currentInfoWindow.value = null
    }
  }

  /**
   * 显示信息窗体
   */
  const showInfoWindow = (marker: any, markerData: Marker) => {
    if (!AMap.value) return

    // 关闭之前的信息窗体
    if (currentInfoWindow.value) {
      currentInfoWindow.value.close()
    }

    // 构建信息窗体内容
    let content = `<div style="padding: 12px; min-width: 200px;">
      <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: bold;">${markerData.title}</h3>`

    if (markerData.poi) {
      if (markerData.poi.address) {
        content += `<p style="margin: 4px 0; color: #666;">📍 ${markerData.poi.address}</p>`
      }
      if (markerData.poi.tel) {
        content += `<p style="margin: 4px 0; color: #666;">📞 ${markerData.poi.tel}</p>`
      }
      if (markerData.poi.type) {
        content += `<p style="margin: 4px 0; color: #999; font-size: 12px;">类型: ${markerData.poi.type}</p>`
      }
    }

    content += '</div>'

    currentInfoWindow.value = new AMap.value.InfoWindow({
      content,
      offset: new AMap.value.Pixel(0, -30)
    })

    currentInfoWindow.value.open(map.value, marker.getPosition())
  }

  /**
   * POI搜索
   */
  const searchPOI = (keyword: string, city?: string): Promise<POI[]> => {
    return new Promise((resolve, reject) => {
      if (!AMap.value) {
        reject(new Error('地图未初始化'))
        return
      }

      AMap.value.plugin('AMap.PlaceSearch', () => {
        const placeSearch = new AMap.value.PlaceSearch({
          city: city || '全国',
          pageSize: 10,
          pageIndex: 1
        })

        placeSearch.search(keyword, (status: string, result: any) => {
          if (status === 'complete' && result.poiList && result.poiList.pois) {
            const pois: POI[] = result.poiList.pois.map((poi: any) => ({
              id: poi.id,
              name: poi.name,
              address: poi.address || '',
              location: {
                lng: poi.location.lng,
                lat: poi.location.lat
              },
              type: poi.type || '',
              tel: poi.tel || ''
            }))
            resolve(pois)
          } else {
            reject(new Error('搜索失败'))
          }
        })
      })
    })
  }

  /**
   * 地理编码
   */
  const geocodeAddress = (address: string, city?: string): Promise<{ lng: number; lat: number }> => {
    return new Promise((resolve, reject) => {
      if (!AMap.value) {
        reject(new Error('地图未初始化'))
        return
      }

      AMap.value.plugin('AMap.Geocoder', () => {
        const geocoder = new AMap.value.Geocoder({
          city: city || '全国'
        })

        geocoder.getLocation(address, (status: string, result: any) => {
          if (status === 'complete' && result.geocodes && result.geocodes.length > 0) {
            const location = result.geocodes[0].location
            resolve({
              lng: location.lng,
              lat: location.lat
            })
          } else {
            reject(new Error('地理编码失败'))
          }
        })
      })
    })
  }

  /**
   * 绘制路线
   */
  const drawRoute = (
    startPos: [number, number],
    endPos: [number, number],
    mode: 'driving' | 'walking' | 'transit' = 'driving'
  ): Promise<any> => {
    return new Promise((resolve, reject) => {
      if (!AMap.value || !map.value) {
        reject(new Error('地图未初始化'))
        return
      }

      let pluginName = ''
      switch (mode) {
        case 'driving':
          pluginName = 'AMap.Driving'
          break
        case 'walking':
          pluginName = 'AMap.Walking'
          break
        case 'transit':
          pluginName = 'AMap.Transfer'
          break
      }

      AMap.value.plugin(pluginName, () => {
        let routeService: any

        if (mode === 'transit') {
          routeService = new AMap.value.Transfer({
            map: map.value,
            panel: undefined
          })
        } else {
          const ServiceClass = mode === 'driving' ? AMap.value.Driving : AMap.value.Walking
          routeService = new ServiceClass({
            map: map.value,
            panel: undefined
          })
        }

        routeService.search(
          new AMap.value.LngLat(...startPos),
          new AMap.value.LngLat(...endPos),
          (status: string, result: any) => {
            if (status === 'complete') {
              resolve(result)
            } else {
              reject(new Error('路线规划失败'))
            }
          }
        )
      })
    })
  }

  /**
   * 设置地图中心
   */
  const setCenter = (center: [number, number], zoom?: number) => {
    if (map.value) {
      map.value.setCenter(center)
      if (zoom) {
        map.value.setZoom(zoom)
      }
    }
  }

  /**
   * 设置城市
   */
  const setCity = (city: string) => {
    if (map.value) {
      map.value.setCity(city)
    }
  }

  /**
   * 计算距离
   */
  const calculateDistance = (pos1: [number, number], pos2: [number, number]): number => {
    if (!AMap.value) return 0

    const p1 = new AMap.value.LngLat(...pos1)
    const p2 = new AMap.value.LngLat(...pos2)
    return p1.distance(p2) // 返回米
  }

  // 生命周期
  onMounted(() => {
    // 组件挂载时不自动初始化，等待外部调用initMap
  })

  onUnmounted(() => {
    // 清理地图实例
    if (map.value) {
      map.value.destroy()
      map.value = null
    }
    isMapReady.value = false
  })

  return {
    // 状态
    map,
    AMap,
    isMapReady,
    markers,

    // 方法
    initMap,
    addMarker,
    addMarkers,
    clearMarkers,
    showInfoWindow,
    searchPOI,
    geocodeAddress,
    drawRoute,
    setCenter,
    setCity,
    calculateDistance
  }
}

