from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient

from datetime import datetime, timedelta
import json

import webbrowser

import os
import fileinput
import base64


# def parse_sleep(resp_json):
#     sleep_data = {}
#
#     for sleep_entry in resp_json["sleep"]:
#         start = sleep_entry['startTime']
#         end = sleep_entry['endTime']
#         # print(f"{sleep_entry['startTime']} to {sleep_entry['endTime']}")
#         start_date = datetime.strptime(start.split("T")[0], "%Y-%m-%d")
#         end_date = datetime.strptime(end.split("T")[0], "%Y-%m-%d")
#
#         start_time = (lambda time: int(time[0]) * 60 + int(time[1]))(
#             start.split("T")[1].split(".")[0].split(":"))
#         end_time = (lambda time: int(time[0]) * 60 + int(time[1]))(end.split("T")[1].split(".")[0].split(":"))
#
#         if start_date == end_date:
#             if str(start_date).split(" ")[0] not in sleep_data:
#                 sleep_data[str(start_date).split(" ")[0]] = np.zeros(1439, dtype=bool)
#             sleep_data[str(start_date).split(" ")[0]][start_time:end_time] = True
#         else:
#             if str(start_date).split(" ")[0] not in sleep_data:
#                 sleep_data[str(start_date).split(" ")[0]] = np.zeros(1439, dtype=bool)
#             if str(end_date).split(" ")[0] not in sleep_data:
#                 sleep_data[str(end_date).split(" ")[0]] = np.zeros(1439, dtype=bool)
#             sleep_data[str(start_date).split(" ")[0]][start_time:1439] = True
#             sleep_data[str(end_date).split(" ")[0]][0:end_time] = True
#
#     return sleep_data


class FitbitAPIAccessor:
    def __init__(self):
        # Set up your client ID and scope:
        # the scope must match that which you requested when you set up your application.
        self.this_app_client_id = "22BFHX"
        self.scope = ["activity", "heartrate", "location", "nutrition",
                      "profile", "settings", "sleep", "social", "weight"]
        self.access_token = None

        self.client = None
        self.fitbit_session = None

    def authenticate(self):
        token = self.get_access_token()
        token_written = False
        for line in fileinput.input(".env", inplace=True):
            if line.split("=")[0].lower() == "token":
                print(f'TOKEN = "{base64.b64encode(json.dumps(token).encode("utf-8")).decode("utf-8")}"')
                token_written = True
            else:
                print(line.rstrip("\n").rstrip("\r"))
        if not token_written:
            with open(".env", "a") as dotenvfile:
                dotenvfile.write(f'TOKEN = "{base64.b64encode(json.dumps(token).encode("utf-8")).decode("utf-8")}"')
        self.set_session(token)
        print("Session with access token created.\n")

    def get_access_token(self):
        """
        Use this to fetch a new token from Fitbit API and set a session with the new token
        :return:
        """
        # Initialize client
        self.client = MobileApplicationClient(self.this_app_client_id)
        fitbit = OAuth2Session(self.this_app_client_id, client=self.client, scope=self.scope)
        authorization_url = "https://www.fitbit.com/oauth2/authorize"

        # Grab the URL for Fitbit's authorization page.
        auth_url, state = fitbit.authorization_url(authorization_url)
        webbrowser.open(auth_url + "&expires_in=31536000")
        print(
            f"\n\nIf a web browser does not open automatically, please open the following link in a browser: {auth_url}"
        )

        # After authenticating, Fitbit will redirect you to the URL you specified in your application settings.
        # It contains the access token.
        while True:
            try:
                callback_url = input("\nPaste URL you get back here: ")
                resp_token = fitbit.token_from_fragment(callback_url)
                break
            except Exception as e:
                print(f"{str(e)}\nFailed to extract token from URL. Press any key to try again, or CTRL+C to stop.")

        print(f"Access token: {resp_token}")
        return resp_token

    def set_session(self, token):
        """
        Use this with a previously acquired token to set a session
        :param token:
        :return:
        """

        self.access_token = token
        self.fitbit_session = OAuth2Session(self.this_app_client_id, client=self.client, scope=["sleep"],
                                            token=self.access_token)

    def get_sleep_data(self):
        # API reference: https://dev.fitbit.com/build/reference/web-api/sleep/
        if self.fitbit_session is None:
            raise ValueError("No session defined, please create session using set_session or get_access_token")

        url = "https://api.fitbit.com/1.2/user/-/sleep/list.json"

        datetime.now()

        # first request
        req_params = {
            "beforeDate": datetime.now().strftime('%Y-%m-%d'),
            "offset": "0",
            "limit": "50",
            "sort": "desc"
        }

        r = self.fitbit_session.get(url, params=req_params)
        resp_json = json.loads(r.content.decode())
        # print(json.dumps(resp_json["pagination"], indent=4, sort_keys=True))

        while True:
            if len(resp_json["sleep"]) > 0:
                with open(os.path.join("responses",
                                       f"sleep_{resp_json['pagination']['beforeDate']}"
                                       f"_offset{resp_json['pagination']['offset']}.json"),
                          "w") as outfile:
                    json.dump(resp_json, outfile)

            print("processing: \n" + json.dumps(resp_json["pagination"], indent=4, sort_keys=True))

            # pprint(self.parse_sleep(resp_json))
            # list_of_list = np.array([self.parse_sleep(resp_json)[key] for key in self.parse_sleep(resp_json)])
            # print(list_of_list)

            if resp_json["pagination"]["next"] == "":
                break

            r = self.fitbit_session.get(resp_json["pagination"]["next"])
            resp_json = json.loads(r.content.decode())

    def save_heart_data(self, destination, start_date=None, days_limit=None):
        """
        Destination will WIPE the target directory - be careful with it!
        :param start_date:
        :param destination: target directory of where the json files should be stored
        :param days_limit: how many days worth of data to get (approximately)
        :return:
        """
        print("\nFetching heart data from Fitbit...", end='')
        # API reference: https://dev.fitbit.com/build/reference/web-api/sleep/
        if self.fitbit_session is None:
            return
        keep_going = True

        if start_date is not None:  # If not given a start date, assume today as start date
            data_date = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            data_date = datetime.now()
        data_date = data_date.replace(month=data_date.month + 1 if data_date.month < 12 else 1,
                                      year=data_date.year + 1 if data_date.month == 12 else data_date.year,
                                      day=1)
        start_date = data_date

        # create destination directory
        if not os.path.exists(destination):
            os.makedirs(destination)

        while keep_going:
            if days_limit is not None:
                if start_date - data_date > timedelta(days=days_limit):
                    break
            keep_going = False  # if no data is present in this month's json, don't keep going

            # print(f"getting {data_date.strftime('%Y-%m-%d')}")
            url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{data_date.strftime('%Y-%m-%d')}/1m.json"
            r = self.fitbit_session.get(url)
            resp_json = json.loads(r.content.decode())

            # iterate over all heart rate data:
            # print(resp_json)
            for activity in resp_json["activities-heart"]:
                # save json to file:
                if len(resp_json["activities-heart"]) > 0:
                    with open(os.path.join(destination,
                                           f"activities-heart_{resp_json['activities-heart'][0]['dateTime']}"
                                           f"-{resp_json['activities-heart'][-1]['dateTime']}.json"),
                              "w") as outfile:
                        json.dump(resp_json, outfile)

                if "restingHeartRate" in activity["value"]:
                    # print(f"found act in {data_date.strftime('%Y-%m-%d')}")
                    keep_going = True

            data_date = data_date.replace(day=1) + timedelta(days=-1)  # go back to the previous month
        print(" Done")
