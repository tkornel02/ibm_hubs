from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator


class CloudantClient:
    def __init__(self, url: str, database: str):
        self.url = url
        self.database = database
        self.authenticator = NoAuthAuthenticator()
        self.client = CloudantV1(self.authenticator)
        self.client.set_service_url(self.url)

    def get_full_response_post_search(self, db: str, ddoc: str, index: str, query: str):
        response = self.client.post_search(db, ddoc, index, query).get_result()

        if len(response.get("rows")) == 0:
            return response

        bookmark = response.get('bookmark')
        while True:
            next_response = self.client.post_search(
                db, ddoc, index, query, bookmark=bookmark).get_result()
            if len(next_response.get("rows")) == 0:
                return response
            response.get('rows').extend(next_response.get("rows"))
            bookmark = next_response.get("bookmark")
