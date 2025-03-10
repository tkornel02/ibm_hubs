from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator
import json

# set no auth, public endpoint
authenticator = NoAuthAuthenticator()
client = CloudantV1(authenticator=authenticator)
client.set_service_url("https://mikerhodes.cloudant.com")

response = client.post_all_docs('airportdb', include_docs=True).get_result()
#print(json.dumps(response, indent=2))

response = client.post_search(
  db='airportdb',
  ddoc='view1',
  index='geo',
  query='lat:[47.3 TO 47.8] AND lon:[19.0 TO 19.5]'
).get_result()

print(json.dumps(response, indent=2))
