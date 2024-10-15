import os
import subprocess
import jwt
from dotenv import load_dotenv
from datetime import datetime

def setup_environment():
    summaries_folder = 'Summaries'
    if not os.path.exists(summaries_folder):
        os.makedirs(summaries_folder)

    load_dotenv()
    valid_token = False
    flowToken = os.environ.get("FLOW_TOKEN")
    if flowToken:
        decoded = jwt.decode(flowToken, options={"verify_signature": False})
        if datetime.fromtimestamp(decoded["exp"]) > datetime.now():
            valid_token = True

    if not valid_token:
        cmd = ["python", "python-app/flow_token.py"]
        subprocess.Popen(cmd).wait()