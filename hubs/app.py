import argparse
from utils import Utils
from cloudant_client import CloudantClient


class App:
    parser = argparse.ArgumentParser(prog="HubCollector")
    url = 'https://mikerhodes.cloudant.com'
    db_name = 'airportdb'

    def __init__(self, client: CloudantClient, lat: float, lon: float, dist: float):

        self.client = client
        self.lat = lat
        self.lon = lon
        self.dist = dist
        Utils.validate_inputs(self.lat, self.lon, self.dist)

    def run(self):
        bounding_box = Utils.calculate_bounding_box_from_inputs(
            self.lat, self.lon, self.dist)

        full_response = self.client.get_full_response_post_search(
            self.db_name,
            ddoc='view1',
            index='geo',
            query=f"lat:[{bounding_box[0]} TO {bounding_box[1]}] AND lon:[{bounding_box[2]} TO {bounding_box[3]}]")

        # sort list based on the distance field
        hub_list = sorted(self.get_hubs_distance_from_response(
            full_response), key=lambda hub: hub['distance'])

        if len(hub_list) == 0:
            print("No hubs found in the given distance")
        else:
            print(f"Hubs within {self.dist} km:")
            for item in hub_list:
                print(
                    f"\"{item.get('name')}\", distance: {item.get('distance')} km")

    # create a hub with "name" and "distance" fields using search response row
    def get_hub_dict_from_row(self, row: dict, lat: float, lon: float) -> dict:
        fields: dict = row.get("fields")
        distance = Utils.calculate_distance_from_coordinates(
            lat, lon, fields.get("lat"), fields.get("lon"))
        hub = {
            "name": fields.get("name"),
            "distance": round(distance, 2)
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
