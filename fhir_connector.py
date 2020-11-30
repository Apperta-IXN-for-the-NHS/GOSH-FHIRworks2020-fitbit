import requests
import json
import copy
from datetime import datetime
from urllib.parse import urljoin


class FhirConnector:
    def __init__(self, fhir_url):
        self.fhir_url = fhir_url
        self.access_token = None
        self.heart_observation_template = {
            "resourceType": "Observation", "id": "heart-rate", "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/vitalsigns"]
            },
            "status": "final", "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }],
                "text": "Vital Signs"
            }],
            "code": {"coding": [{"system": "http://loinc.org", "code": "40443-4", "display": "Heart rate Resting"}],
                     "text": "Heart rate Resting"},
            "subject": {"reference": "Patient/None"},  # to modify
            "effectiveDateTime": "2000-01-01T00:00:00.000+00:00",  # to modify
            "issued": "2000-01-01T00:00:00.000+00:00",  # to modify
            "valueQuantity": {
                "value": 0,  # to modify
                "unit": "beats/minute",
                "system": "http://unitsofmeasure.org",
                "code": "/min"
            }
        }

    def test(self, patient_id: str, effective_dt: datetime, issued_dt: datetime, value):
        print(patient_id, effective_dt, issued_dt, value)

    def push_heart_rate_observation(self, patient_id: str, effective_dt: datetime, issued_dt: datetime, value):
        observation = copy.deepcopy(self.heart_observation_template)
        observation['subject']["reference"] = f"Patient/{patient_id}"
        observation["effectiveDateTime"] = effective_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        observation["issued"] = issued_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        observation["valueQuantity"]["value"] = value
        # print(observation)
        r = requests.post(urljoin(self.fhir_url, "Observation"),
                          data=json.dumps(observation),
                          headers={
                              'Authorization': f'Bearer {self.access_token}',
                              'Content-Type': 'application/fhir+json',
                          })
        # print(r.status_code)
        # print(r.json()["id"])
        resp_json = json.loads(r.content.decode())
        if r.status_code == 201 and "id" in resp_json:
            return {"status": "success", "observation_id": resp_json["id"]}
        else:
            return resp_json

    def get_access_token(self, TOKEN_URL, CLIENT_ID, CLIENT_SECRET, SCOPE):
        r = requests.post(TOKEN_URL,
                          f"grant_type=client_credentials"
                          f"&client_id={CLIENT_ID}"
                          f"&client_secret={CLIENT_SECRET}"
                          f"&scope={SCOPE}"
                          , headers={'content-type': "application/x-www-form-urlencoded"})

        if r.content != '' and r.status_code == 200:
            resp_json = json.loads(r.content.decode())
            return resp_json.get('access_token', None)
        else:
            return {'error': 'failed to acquire access token'}

    def authenticate(self, TOKEN_URL, CLIENT_ID, CLIENT_SECRET, SCOPE):
        token = self.get_access_token(TOKEN_URL, CLIENT_ID, CLIENT_SECRET, SCOPE)
        if "error" not in token:
            self.access_token = token
        else:
            raise ValueError(
                "Could not authenticate/acquire access token. \n"
                "Please ensure to provide TOKEN_URL, CLIENT_ID, CLIENT_SECRET, SCOPE and FHIR_URL in the .env file")
