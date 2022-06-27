import json
import logging
import sys
import time

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
    print(respdict)
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
    logging.info(f"Resources: {resources}")


def calculate_args(test_name, args):
    for k, v in resources.items():
        for k2, v2 in args.items():
            if type(v2) == str and f"${k}" in v2:
                try:
                    args[k2] = v2.replace(f"${k}", v)
                    logging.info(f"New value for {k2}: {args[k2]}")
                except KeyError:
                    logging.error(
                        "Test {test_name} failed. {k} not found when calculating args"
                    )
            elif type(v2) == dict:
                calculate_args(test_name, v2)


def calculate_link(link):
    if type(link) == list:
        nlink = ""
        for l in link:
            if "$" in l:
                l = resources[l[1:]]
            nlink += l
        link = nlink
    return link


def run_request(testdict):

    name = testdict["name"]
    reqtype = testdict["req_type"]
    link = testdict["link"]
    pass_msgs = testdict.get("pass", [])
    store = testdict.get("store", None)
    args = testdict.get("args", {})
    logging.info(f"Running {name} test")

    link = calculate_link(link)
    calculate_args(name, args)
    logging.info(f"Running {reqtype} on {URL}{link} with args {args}")
    if reqtype == "post":
        resp = requests.post(f"{URL}{link}", json=args, headers=header)
    elif reqtype == "get":
        resp = requests.get(f"{URL}{link}", json=args, headers=header)
    elif reqtype == "delete":
        resp = requests.delete(f"{URL}{link}", json=args, headers=header)
    resdict = resp.json()
    message = resdict["message"]
    if len(pass_msgs) > 0 and message in pass_msgs:
        logging.info(f"Test {name} passed with message: {message}")
    else:
        logging.error(f"Test {name} failed with message: {message}")
        exit()
    if store:
        calculate_store(name, store, resdict)


def wait_until(testdict):

    name = testdict["name"]
    reqtype = testdict["req_type"]
    link = testdict["link"]
    args = testdict.get("args", {})
    link = calculate_link(link)
    calculate_args(name, args)
    timeout = testdict.get("timeout", 60)
    sleep = testdict.get("sleep", 3)
    condition = testdict["condition"]
    ckey = condition["key"]
    cval = condition["value"]
    if type(cval) == str:
        cval = [cval]

    logging.info(f"Running {name} test")

    if reqtype == "post":
        func = requests.post
    elif reqtype == "get":
        func = requests.get

    tm = 0
    while tm < timeout:
        resp = func(f"{URL}{link}", json=args, headers=header)
        resdict = resp.json()
        if resdict[ckey] in cval:
            logging.info(f"Condition met {ckey} = {resdict[ckey]}")
            return
        logging.info(f"Condition not yet met {ckey} = {resdict[ckey]}")
        time.sleep(sleep)
        tm += sleep


def run_test(testdict):
    test_type = testdict.get("test_type", "request")
    if test_type == "request":
        run_request(testdict)
    elif test_type == "wait_until":
        wait_until(testdict)


if __name__ == "__main__":

    test_json = sys.argv[1]
    with open(test_json) as f:
        test = json.load(f)

    if "register" in test and not register(test["register"]):
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
