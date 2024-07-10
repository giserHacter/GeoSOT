#Author:Peter Hsu
#Time: July 10, 2024


import os
import geopandas as gpd
import time
import s2sphere
import h3

def encode_point_with_level(lat, lng, level):
    # 创建一个S2LatLng对象
    latlng = s2sphere.LatLng.from_degrees(lat, lng)
    
    # 获取指定级别的S2CellId
    cell_id = s2sphere.CellId.from_lat_lng(latlng).parent(level)
    
    return cell_id.to_token()

# unit in meters
# 1 degree = D˚×πR/180˚
radius=6371000
Z_extent=512*3.141592653589793*radius/180
height_extent=50000000


def GeoSoT_encode_3D_96bits(lat, lon, height,level):
    """encode spatial coordinates to GeoSoT format based on Binary three-dimensional code
    reference:ISPRS Int. J. Geo-Inf. 2021, 10, 489
    three digits for a group: e.g., altitude-lat-lon
    """
    strip=2**level
    lat_normal=int((lat+90)/180*strip)
    lon_normal=int((lon+180)/360*strip)
    height_normal=int(height/height_extent*strip)

    # 32 bits
    # lat_normal_32bit = format(lat_normal, '032b')
    # lon_normal_32bit = format(lon_normal, '032b')
    # height_normal_32bit = format(height_normal, '032b')

    combined=0
    for i in range(32):
        combined |= ((lon_normal >> i) & 1) << (3 * i)
        combined |= ((lat_normal >> i) & 1) << (3 * i + 1)
        combined |= ((height_normal >> i) & 1) << (3 * i + 2)
    

    return combined

def GeoSoT_encode_2D_96bits(lat, lon,level):
    """encode spatial coordinates to GeoSoT format based on Binary three-dimensional code
    reference:ISPRS Int. J. Geo-Inf. 2021, 10, 489
    three digits for a group: e.g., altitude-lat-lon
    """
    strip=2**level
    lat_normal=int((lat+90)/180*strip)
    lon_normal=int((lon+180)/360*strip)

    # 32 bits
    # lat_normal_32bit = format(lat_normal, '032b')
    # lon_normal_32bit = format(lon_normal, '032b')
    # height_normal_32bit = format(height_normal, '032b')

    combined=0
    for i in range(32):
        combined |= ((lon_normal >> i) & 1) << (3 * i)
        combined |= ((lat_normal >> i) & 1) << (3 * i + 1)
    

    return combined

def GeoSoT_encode_3D_32bits(lat, lon, height, level):
    """encode spatial coordinates to GeoSoT format based on Binary three-dimensional code
    reference:ISPRS Int. J. Geo-Inf. 2021, 10, 489
    three digits for a group: e.g., altitude-lat-lon
    """

    if level>31:
        print("level too large")
        return 0
    
    encode_str="G"
    strip=2**level

    # if the lat=90 or lon=180 or height=height_extent need to reduce 1
    lat_normal=int((lat+90)/180*strip)
    lon_normal=int((lon+180)/360*strip)
    height_normal=int(height/height_extent*strip)

    # Convert to binary strings
    lat_bin = format(lat_normal, f'0{level}b')
    lon_bin = format(lon_normal, f'0{level}b')
    height_bin = format(height_normal, f'0{level}b')

    for i in range(level):
        if i==9 or i==15:
            encode_str+="-"
        elif i==21:
            encode_str+="."

        
        encode_str+=geo_sot_encode(lat_bin[i], lon_bin[i], height_bin[i])

    return encode_str
def create_lookup_table():
    """创建一个包含所有可能编码值的查找表"""
    return ["0", "1", "2", "3", "4", "5", "6", "7"]

def geo_sot_encode(lat_code, lng_code, alt_code):
    """根据经度、纬度和高度的二进制编码选择相应的值"""
    lookup_table = create_lookup_table()

    # 将二进制编码转换为整数
    lat_idx = int(lat_code, 2)
    lng_idx = int(lng_code, 2)
    alt_idx = int(alt_code, 2)

    # 计算索引
    index = (alt_idx << 2) | (lat_idx << 1) | lng_idx
    return lookup_table[index]


def test_point(point_path):
    # Load the shapefile
    gdf = gpd.read_file(point_path)

    # Extract the coordinates of the points
    coordinates = gdf.geometry.apply(lambda geom: (geom.x, geom.y,geom.z))
     
    time1=time.time()
    for i, (x, y, z) in enumerate(coordinates):
        aa=GeoSoT_encode_2D_96bits(y, x,  27)  # level 16 for 51
    
    time2=time.time()
    print(f'Point coordinate processing time: {time2-time1} seconds')

    time1=time.time()
    for i, (x, y, z) in enumerate(coordinates):
        s2_token = encode_point_with_level(y, x, 26)
    
    time2=time.time()
    print(f'Point coordinate processing time: {time2-time1} seconds')

    time1=time.time()
    for i, (x, y, z) in enumerate(coordinates):
        h3_token = h3.geo_to_h3(y, x, 15)
    
    time2=time.time()
    print(f'Point coordinate processing time: {time2-time1} seconds')



if __name__ == "__main__":
    point_path=r'E:\test\research\points.shp'
    line_path=r'E:\test\research\line_segments.shp'
    polygon_path=r'E:\test\research\random_squares.shp'

    
    # test_point(point_path)
    print(GeoSoT_encode_3D_32bits(45,77,100,31))

    
    
