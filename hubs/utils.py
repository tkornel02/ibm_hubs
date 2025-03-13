import math
import haversine as hs


class Utils:
    @staticmethod
    def validate_inputs(lat: float, lon: float, dist: float):
        if not (-90 < lat < 90 and -180 < lon < 180 and 0 <= dist):
            raise ValueError(
                "Invalid values. Enter latitude between -90 and 90 degrees, longitude between -180 and 180 degrees, and distance greater than 0 km")

    @staticmethod
    def calculate_bounding_box_from_inputs(lat: float, lon: float, dist: float) -> list:
        buffer_lat = dist/111.0
        buffer_lon = dist/(111.0*math.cos(math.radians(lat)))
        return [lat-buffer_lat, lat+buffer_lat, lon-buffer_lon, lon+buffer_lon]

    @staticmethod
    def calculate_distance_from_coordinates(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        return hs.haversine(point1, point2)
