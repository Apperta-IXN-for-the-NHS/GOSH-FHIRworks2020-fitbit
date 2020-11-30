# Deployment instructions
## Installing requirements
- Using a virtual environment is recommended
    * Under Windows:
        * Create the virtual environment using `py -m venv venv`
        * Activate the venv: `venv\Scripts\activate`
    * Under Linux
        * Create the virtual environment by first installing the dependencies:
            * `sudo apt update`
            * `sudo apt install python3.7-dev python3.7-venv`
        * Create the virtual environment: `python3.7 -m venv venv`
        * Activate the venv: `source venv/bin/activate`
    * To leave the venv, use `deactivate`

- Install dependencies:
    * Linux: `python -m pip install -r requirements.txt` inside the venv
    * Windows: `py -m pip install -r requirements.txt`
        
## Configuring environment variables
* Copy `.env.template` to `.env`
* Fill out `.env` with proper data

```
CLIENT_ID = "0f6332f4-c060-49fc-bcf6-548982d56569"
CLIENT_SECRET = "ux@CJAaxCD85A9psm-Wdb?x3/Z4c6gp9"
SCOPE = "https://gosh-fhir-synth.azurehealthcareapis.com/.default"
TOKEN_URL = "https://login.microsoftonline.com/ca254449-06ec-4e1d-a3c9-f8b84e2afe3f/oauth2/v2.0/token"
FHIR_URL = "https://gosh-fhir-synth.azurehealthcareapis.com"
target_patient_id = "49df1158-093c-47c4-85c7-5b297093880e"
```

## Get data from Fitbit and post to FHIR server
#### Running for the first time: `python main.py`

* If using a desktop environment, a browser tab will open asking to log in with Fitbit
    * **A graphical user interface is required on this step in order to log into Fitbit and acquire an access token.**
    * A mobile phone should suffice if no graphical environment is available on the computer.
* Once logged in, the browser will point to localhost. Copy the URL from the browser and paste back into the terminal.
* The program is now POSTing heart rate observations to the patient specified in `.env`

#### Running again: same command `python main.py`
* The browser shouldn't open again this time, 
and instead, the program will immediately start dumping data from Fitbit into FHIR


## More granular control + graphing with the API
If you wish to have more granular control over the range of the data to push, or wish to do more manipulation with the
data from Fitbit, you can run the API server to fetch data from Fitbit.

#### Running the API server: `uvicorn api:app`
Server will be made available on localhost on port 8000.

A list of endpoints is available at the root.

Endpoints ending in `/graph` will return a PNG image with the data from the endpoint, graphed with Matplotlib.