from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator
import math, argparse
import haversine as hs

class App:
    parser = argparse.ArgumentParser(prog="HubCollector")
    url = 'https://mikerhodes.cloudant.com'
    db_name = 'airportdb'

    def __init__(self):
        self.setup_argparser()
        self.lat = self.args.lat
        self.lon = self.args.lon
        self.dist = self.args.dist
        self.validate_inputs()
        self.setup_client()

    def setup_argparser(self):
        self.parser.add_argument(
            '--lat', type=float, help='latitude of location to measure distance from')
        self.parser.add_argument(
            '--lon', type=float, help='longitude of location to measure distance from')
        self.parser.add_argument('--dist', type=float,
                                 help='max distance of hubs')
        self.args = self.parser.parse_args()

    def setup_client(self):
        self.authenticator = NoAuthAuthenticator()
        self.client = CloudantV1(self.authenticator)
        self.client.set_service_url(self.url)

    def validate_inputs(self):
        if not (-90 < self.lat < 90 and -180 < self.lon < 180 and 0 <= self.dist):
            raise ValueError("Invalid CLI arguments.")

    def run(self):
        bounding_box = self.calculate_bounding_box_from_inputs()

        response = self.client.post_search(
            db=self.db_name,
            ddoc='view1',
            index='geo',
            query=f"lat:[{bounding_box[0]} TO {bounding_box[1]}] AND lon:[{bounding_box[2]} TO {bounding_box[3]}]"
        ).get_result()

        # sort list based on the distance field
        hub_list = sorted(self.get_hubs_distance_from_response(
            response), key=lambda hub: hub['distance'])

        if len(hub_list) == 0:
            print("No hubs found in the given distance")
        else:
            print("Hubs")
            for item in hub_list:
                print(
                    f"\"{item.get('name')}\", distance: {item.get('distance')} km")

    # create an approximation bounding box from CLI args
    def calculate_bounding_box_from_inputs(self) -> list:
        buffer_lat = self.dist/111.0
        buffer_lon = self.dist/(111.0*math.cos(math.radians(self.lat)))
        return [self.lat-buffer_lat, self.lat+buffer_lat, self.lon-buffer_lon, self.lon+buffer_lon]

    # calculate distance using the haversine method
    def calculate_distance_from_coordinates(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        return hs.haversine(point1, point2)

    # create a hub with "name" and "distance" fields using search response row
    def get_hub_dict_from_row(self, row: dict, lat: float, lon: float) -> dict:
        fields: dict = row.get("fields")
        hub = {
            "name": fields.get("name"),
            "distance": round(self.calculate_distance_from_coordinates(lat, lon, fields.get("lat"), fields.get("lon")), 2)
        }
        return hub

    # create an unsorted list of the hubs that are in the given distance range
    def get_hubs_distance_from_response(self, response: dict) -> list:
        hubs_list = []
        for row in response.get("rows"):
            hub = self.get_hub_dict_from_row(row, self.lat, self.lon)
            if (hub.get("distance") <= self.dist):
                hubs_list.append(hub)
        return hubs_list


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()
