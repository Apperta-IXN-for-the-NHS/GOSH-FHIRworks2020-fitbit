from fhir_connector import FhirConnector
from fetch_data import FitbitAPIAccessor
from process_data import process_heart_json_files
import os
from dotenv import load_dotenv
from datetime import datetime
import json

from tqdm import tqdm
import base64

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SCOPE = os.getenv("SCOPE")
TOKEN_URL = os.getenv("TOKEN_URL")

FHIR_URL = os.getenv("FHIR_URL")

# We are using a fixed patient ID because we aren't allowed to
# create new Patients with the given API
target_patient_id = os.getenv("target_patient_id")


def fetch_and_post(temp_json_directory="json_responses", start_date=None, days_limit=None):
    fitbit_access.save_heart_data(temp_json_directory, start_date, days_limit)
    resting_hr, activity = process_heart_json_files(temp_json_directory)

    # convert string date to datetime objects. Makes it easier to change format later on while posting to fhir
    # resting_hr = [(datetime.strptime(entry[0], "%Y-%m-%d"), entry[1]) for entry in resting_hr]
    print("\nSending data to FHIR...")
    for (date, val) in tqdm(resting_hr.items()):
        date = datetime.strptime(date, "%Y-%m-%d")
        fhir_poster.push_heart_rate_observation(target_patient_id, date, date, val)
    print("\nAll done!\n")


fitbit_access = FitbitAPIAccessor()
if os.getenv("TOKEN") is None:
    fitbit_access.authenticate()
else:
    fitbit_access.set_session(json.loads(base64.b64decode(os.getenv("TOKEN"))))

fhir_poster = FhirConnector(FHIR_URL)
fhir_poster.authenticate(TOKEN_URL, CLIENT_ID, CLIENT_SECRET, SCOPE)

if __name__ == "__main__":
    fetch_and_post()
