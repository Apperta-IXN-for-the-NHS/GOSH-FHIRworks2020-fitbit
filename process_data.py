import os
import json
from tqdm import tqdm


def process_heart_json_files(file_or_path, single_file=False):
    activities_heart = []
    if not single_file:
        for file in os.listdir(file_or_path):
            with open(os.path.join(file_or_path, file), "r", encoding="utf-8") as jsonfile:
                activities_heart += json.load(jsonfile)["activities-heart"]

    resting_heartrate = {}
    activities = {}
    print("Processing heart data...")
    for activity in tqdm(activities_heart):
        if "restingHeartRate" in activity["value"]:
            resting_heartrate[activity['dateTime']] = activity['value']['restingHeartRate']

        idle_t, fb_t, cd_t, pk_t = 0, 0, 0, 0
        idle_c, fb_c, cd_c, pk_c = 0, 0, 0, 0
        for heartRateZone in activity["value"]["heartRateZones"]:
            if "minutes" in heartRateZone:
                if heartRateZone["name"] == "Fat Burn":
                    fb_t = heartRateZone["minutes"]
                elif heartRateZone["name"] == "Cardio":
                    cd_t = heartRateZone["minutes"]
                elif heartRateZone["name"] == "Peak":
                    pk_t = heartRateZone["minutes"]
                elif heartRateZone["name"] == "Out of Range":
                    idle_t = heartRateZone["minutes"]
            if "caloriesOut" in heartRateZone:
                if heartRateZone["name"] == "Fat Burn":
                    fb_c = heartRateZone["caloriesOut"]
                elif heartRateZone["name"] == "Cardio":
                    cd_c = heartRateZone["caloriesOut"]
                elif heartRateZone["name"] == "Peak":
                    pk_c = heartRateZone["caloriesOut"]
                elif heartRateZone["name"] == "Out of Range":
                    idle_c = heartRateZone["caloriesOut"]
        activities[activity['dateTime']] = {
            "time_in_zones": {
                "idle": idle_t, "fatburn": fb_t,
                "cardio": cd_t, "peak": pk_t
            },
            "calories_in_zones":
                {
                    "idle": idle_c, "fatburn": fb_c,
                    "cardio": cd_c, "peak": pk_c
                }
        }

    return resting_heartrate, activities

# from fetch_data import FitbitAPIAccessor
# import numpy as np
# import matplotlib.pyplot as plt
# from datetime import datetime
# fitbit_data = FitbitAPIAccessor()

# fitbit_data.get_access_token()
# fitbit_data.set_session({
#     'access_token': 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMkJGSFgiLCJzdWIiOiI2Wk5GTUgiLCJpc3MiOiJGa'
#                     'XRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3aHIgd3BybyB3bnV0IHdzbGU'
#                     'gd3dlaSB3c29jIHdzZXQgd2FjdCB3bG9jIiwiZXhwIjoxNjE0NzA2MjEyLCJpYXQiOjE1ODQ1O'
#                     'DU0NDh9.VAV1PBnhwa2m_zcZjIJ_LFrseVsoDz4nwLmTBU-PeoU',
#     'user_id': '6ZNFMH',
#     'scope': ['location', 'settings', 'heartrate', 'weight', 'sleep', 'profile', 'nutrition',
#               'social', 'activity'],
#     'state': 'nUYl9TY0COJrzyKNSAuHq5mPFxfIhA',
#     'token_type': 'Bearer', 'expires_in': 30120764, 'expires_at': 1614706224.407847})

# a = {
#     'access_token': 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMkJGSFgiLCJzdWIiOiI2S1pQQjkiLCJpc3MiOiJGa'
#                     'XRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3aHIgd3BybyB3bnV0IHdzbGU'
#                     'gd3dlaSB3c29jIHdhY3Qgd3NldCB3bG9jIiwiZXhwIjoxNTg0ODM2OTI4LCJpYXQiOjE1ODQ3N'
#                     'TExNjN9.L7EIhMplmZFtHYfnxjNgKDrEdtf5bTgMMj_vxRnZ_F0',
#     'user_id': '6KZPB9',
#     'scope': ['sleep', 'activity', 'heartrate', 'settings', 'profile', 'weight', 'nutrition',
#               'social', 'location'],
#     'state': 'zw9Mdc9VpxUBo0cG3ysYFnBcphuYBu',
#     'token_type': 'Bearer',
#     'expires_in': 85765
# }
# fitbit_data.set_session(a)
#
# # fitbit_data.get_sleep_data()
# fitbit_data.save_heart_data("json_responses")
# rh, act = process_heart_json_files("json_responses")
#
# rh.sort(key=lambda tup: datetime.strptime(tup[0], "%Y-%m-%d"))
# act.sort(key=lambda tup: datetime.strptime(tup[0], "%Y-%m-%d"))
#
# plt.xticks(np.arange(0, len(rh) - 1, 28), rotation='vertical')
# plt.plot(*zip(*rh))
#
# plt.show()
#
# plt.xticks(np.arange(0, len(act) - 1, 28), rotation='vertical')
# plt.stackplot([e[0] for e in act], *zip(*[e[1][0] for e in act]), colors=['g', 'orange', 'r', 'pink'])
# plt.show()
#
# plt.xticks(np.arange(0, len(act) - 1, 28), rotation='vertical')
# plt.stackplot([e[0] for e in act], *zip(*[e[1][1] for e in act]), colors=['g', 'orange', 'r', 'pink'])
# plt.show()
#
# plt.savefig("foo.png", dpi=600)
