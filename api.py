from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from main import fetch_and_post, fitbit_access
from process_data import process_heart_json_files
from uuid import uuid4
from datetime import datetime
import os

import matplotlib.pyplot as plt
import numpy as np

app = FastAPI()
if not os.path.exists("graphs"):
    os.makedirs("graphs")
temp_json_target_root = "api_json_tmp"


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """<h4>GOSH-FHIRworks2020-fitbit API</h4>
<p>API endpoints:</p>
<ul>
    <li><a href='/heart'>/heart</a></li>
    
    <li><a href='/heart/resting'>/heart/resting</a></li>
    <li><a href='/heart/resting/graph'>/heart/resting/graph</a></li>
    
    <li><a href='/heart/activity'>/heart/activity</a></li>
    
    <li><a href='/heart/activity/calories'>/heart/activity/calories</a></li> <li><a 
    href='/heart/activity/calories/graph'>/heart/activity/calories/graph</a></li> <li><a 
    href='/heart/activity/time'>/heart/activity/time</a></li> <li><a 
    href='/heart/activity/time/graph'>/heart/activity/time/graph</a></li> </ul> <br> <p>Parameters:</p> <ul> 
    <li>start_date: date from which to start collecting data from (YYYY-MM-DD). If not specified, start from today. 
    Approximate</li> <li>days_limit: max number of days to get data for. If not specified, keep going until there is 
    no data. Approximate</li> </ul> """


@app.get("/heart")
def all_heart_data(start_date: str = None, days_limit: int = None):
    """
    Get both activity and resting heart rate
    :param start_date:
    :param days_limit:
    :return:
    """
    temp_json_target = os.path.join(temp_json_target_root, str(uuid4()))
    fitbit_access.save_heart_data(temp_json_target, start_date, days_limit)
    resting_hr, activity = process_heart_json_files(temp_json_target)

    return {
        "resting_heart_rate": resting_hr,
        "heart_activity": activity
    }


@app.get("/heart/resting/graph")
def generate_graph(start_date: str = None, days_limit: str = None):
    temp_json_target = os.path.join(temp_json_target_root, str(uuid4()))
    fitbit_access.save_heart_data(temp_json_target, start_date, days_limit)
    rh, _ = process_heart_json_files(temp_json_target)

    plt.xticks(np.arange(0, len(rh) - 1, 28), rotation='vertical')
    plt.plot(*zip(*[(date, value) for (date, value) in rh.items()]))

    filename = str(uuid4()) + ".png"
    plt.savefig(os.path.join("graphs", filename), dpi=600)

    return FileResponse(os.path.join("graphs", filename))


@app.get("/heart/{data_type}")
def heart_data_stype(data_type: str = None, start_date: str = None, days_limit: int = None):
    """
    :param data_type: select between 'resting' and 'activity'
    :param start_date: Date from which to start getting data from (going back in time) (approximate)
    :param days_limit: how many days to fetch for (approximately)
    :return:
    """
    data_type = data_type.lower()
    if data_type == "resting" or data_type == "activity":
        temp_json_target = os.path.join(temp_json_target_root, str(uuid4()))
        fitbit_access.save_heart_data(temp_json_target, start_date, days_limit)
        resting_hr, activity = process_heart_json_files(temp_json_target)

        if data_type == "resting":
            return resting_hr
        else:
            return activity


@app.get("/heart/{data_type}/{act_type}")
def heart_data_stype(data_type: str, act_type: str, start_date: str = None, days_limit: int = None):
    """
    :param act_type:
    :param data_type: select between 'resting' and 'activity'
    :param start_date: Date from which to start getting data from (going back in time) (approximate)
    :param days_limit: how many days to fetch for (approximately)
    :return:
    """
    data_type = data_type.lower()
    act_type = act_type.lower()
    if data_type == "activity":
        temp_json_target = os.path.join(temp_json_target_root, str(uuid4()))
        fitbit_access.save_heart_data(temp_json_target, start_date, days_limit)
        resting_hr, activity = process_heart_json_files(temp_json_target)

        if act_type == "calories":
            return_json = {}
            for key, val in activity.items():
                return_json[key] = val["calories_in_zones"]
            return return_json
        elif act_type == "time":
            print("TIME TIME!")
            return_json = {}
            for key, val in activity.items():
                return_json[key] = val["time_in_zones"]
            return return_json
        else:
            raise HTTPException(status_code=404, detail="Endpoint not found")
    else:
        raise HTTPException(status_code=404, detail="Endpoint not found")


@app.get('/heart/activity/{act_type}/graph')
def heart_act_graph(act_type: str = None, start_date: str = None, days_limit: int = None):
    temp_json_target = os.path.join(temp_json_target_root, str(uuid4()))
    fitbit_access.save_heart_data(temp_json_target, start_date, days_limit)
    _, act = process_heart_json_files(temp_json_target)
    if act_type.lower() == 'calories':
        act_type_key = 'calories_in_zones'
    elif act_type.lower() == 'time':
        act_type_key = 'time_in_zones'
    else:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    fig, ax = plt.subplots(1, 1)
    ax.xaxis_date()
    ax.tick_params(axis='x', rotation=35)
    plt.stackplot([datetime.strptime(date, "%Y-%m-%d") for date in act.keys()],
                  *zip(*[
                      (
                          float(act_entry["idle"]),
                          float(act_entry["fatburn"]),
                          float(act_entry["cardio"]),
                          float(act_entry["peak"])
                      )
                      for act_entry in
                      [act[date][act_type_key] for date in act.keys()]
                  ]),
                  colors=['g', 'orange', 'r', 'pink'])

    filename = str(uuid4()) + ".png"
    plt.savefig(os.path.join("graphs", filename), dpi=600)

    return FileResponse(os.path.join("graphs", filename))
