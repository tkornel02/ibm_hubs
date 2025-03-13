import argparse
from app import App
from cloudant_client import CloudantClient


class CLIApp:
    url = 'https://mikerhodes.cloudant.com'
    database = 'airportdb'

    def __init__(self):
        self.setup_argparser()
        self.setup_client()
        self.setup_app()

    def setup_argparser(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '--lat', type=float, help='latitude of location to measure distance from', required=True)
        self.parser.add_argument(
            '--lon', type=float, help='longitude of location to measure distance from', required=True)
        self.parser.add_argument('--dist', type=float,
                                 help='max distance of hubs', required=True)
        self.args = self.parser.parse_args()

    def setup_client(self):
        self.client = CloudantClient(self.url, self.database)

    def setup_app(self):
        self.app = App(self.client, self.args.lat,
                       self.args.lon, self.args.dist)

    def run(self):
        self.app.run()


if __name__ == '__main__':
    cli_app = CLIApp()
    cli_app.run()
