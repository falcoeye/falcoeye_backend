import json
import logging
import sys

import requests
from falcoeye_kubernetes import FalcoServingKube

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# backend_kube = FalcoServingKube("falcoeye-backend")
# backend_server = backend_kube.get_service_address(external=True,hostname=True)
# URL = f"http://{backend_server}"
URL = "http://0.0.0.0:5000"
logging.info(f"backend server: {URL}")


def register(regdict):
    args = regdict["args"]
    logging.info(f"Registering {args['email']}")
    res = requests.post(f"{URL}/auth/register", json=args)
    resdict = res.json()
    message = resdict["message"]
    if message in regdict["pass"]:
        logging.info(f"Registration passed with message: {message}")
        return True
    else:
        logging.error(f"Registration failed with message: {message}")
        return False


def login(regdict):
    args = regdict["args"]
    logging.info(f"Logging in with {args['email']}")
    res = requests.post(f"{URL}/auth/login", json=args)
    resdict = res.json()
    message = resdict["message"]
    if message in regdict["pass"]:
        logging.info(f"Logging in passed with message: {message}")
        return resdict["access_token"]
    else:
        logging.error(f"Logging in failed with message: {message}")
        return False


def calculate_store(test_name, store, respdict):

    for k, cal in store.items():
        success = True
        value = None
        for node in cal:
            if node["type"] == "dict":
                if node["from"] == "response":
                    value = respdict[node["key"]]
                elif node["from"] == "value":
                    value = value[node["key"]]
            elif node["type"] == "list":
                if "index" in node:
                    value = value[node["index"]]
                else:
                    condition = node["condition"]
                    ckey = condition["key"]
                    cval = condition["value"]
                    t_success = False
                    for c in value:
                        if c[ckey] == cval:
                            value = c
                            t_success = True
                            break
                    if not t_success:
                        success = False
                        break
        if not success:
            logging.error(
                f"Test {test_name} failed. Couldn't calculate store value {k}"
            )
            exit()
        resources[k] = value
        logging.info(f"Caluclated value for {k} {value}")


def calculate_args(test_name, args):
    for k, v in args.items():
        if v[0] == "$":
            try:
                args[k] = resources[v[1:]]
            except KeyError:
                logging.error(
                    "Test {test_name} failed. {k} not found when calculating args"
                )


def run_test(testdict):

    name = testdict["name"]
    reqtype = testdict["type"]
    link = testdict["link"]
    pass_msgs = testdict["pass"]
    store = testdict.get("store", None)
    args = testdict.get("args", {})
    logging.info(f"Running {name} test")

    calculate_args(name, args)

    if reqtype == "post":
        print(f"{URL}{link}")
        resp = requests.post(f"{URL}{link}", json=args, headers=header)
    elif reqtype == "get":
        resp = requests.get(f"{URL}{link}", json=args, headers=header)
    resdict = resp.json()
    message = resdict["message"]
    if message in pass_msgs:
        logging.info(f"Test {name} passed with message: {message}")
    else:
        logging.error(f"Test {name} failed with message: {message}")
        exit()
    if store:
        calculate_store(name, store, resdict)


if __name__ == "__main__":

    test_json = sys.argv[1]
    with open(test_json) as f:
        test = json.load(f)

    if not register(test["register"]):
        exit()

    if not (access_token := login(test["login"])):
        exit()

    header = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": access_token,
    }
    resources = {}
    for t in test["tests"]:
        run_test(t)
