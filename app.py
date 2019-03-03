#!flask/bin/python

# Libraries
from pprint import pprint
from flask import Flask
from flask import json
from flask import request
from flask import render_template
import sys, getopt
import json
import requests

############## USER DEFINED SETTINGS ###############
# MERAKI SETTINGS
validator = "5e12053e6a917d0e49e877d03728bfd421767c19"
secret = "aman"
version = "2.0"  # This code was written to support the CMX JSON version specified
locationdata = "Location Data Holder"
null = None
####################################################
app = Flask(__name__)


# Respond to Meraki with validator


@app.route("/", methods=["GET"])
def get_validator():
    print("validator sent to: ", request.environ["REMOTE_ADDR"])
    return validator


# Accept CMX JSON POST


@app.route("/", methods=["POST"])
def get_locationJSON():
    global locationdata

    if not request.json or not "data" in request.json:
        return ("invalid data", 400)

    locationdata = request.json
    # pprint(locationdata, indent=1)
    print("Received POST from ", request.environ["REMOTE_ADDR"])

    # Verify secret
    if locationdata["secret"] != secret:
        print("secret invalid:", locationdata["secret"])
        return ("invalid secret", 403)

    else:
        print("secret verified: ", locationdata["secret"])

    # Verify version
    if locationdata["version"] != version:
        print("invalid version")
        return ("invalid version", 400)

    else:
        print("version verified: ", locationdata["version"])

    # Determine device type
    if locationdata["type"] == "DevicesSeen":
        print("WiFi Devices Seen")
        # print(locationdata)
        print('Sending Post request')
        requests.get("http://2019.almafiesta.com/testing2019/location.php", data=locationdata)

    elif locationdata["type"] == "BluetoothDevicesSeen":
        print("Bluetooth Devices Seen")
    else:
        print("Unknown Device 'type'")
        return ("invalid device type", 403)

    # Return success message
    return "Location Scanning POST Received"


@app.route("/go/", methods=["GET"])
def get_go():
    return render_template("index.html", **locals())


@app.route("/clients/", methods=["GET"])
def get_clients():
    global locationdata
    if locationdata != "Location Data Holder":
        return render_template("clients.html", observations=locationdata["data"]["observations"])

    return ""


@app.route("/clients/<clientMac>", methods=["GET"])
def get_individualclients(clientMac):
    global locationdata
    for client in locationdata["data"]["observations"]:
        if client["clientMac"] == clientMac:
            return json.dumps(client)

    return ""


# Launch application with supplied arguments
def main(argv):
    global validator
    global secret

    try:
        opts, args = getopt.getopt(argv, "hv:s:", ["validator=", "secret="])
    except getopt.GetoptError:
        print("locationscanningreceiver.py -v <validator> -s <secret>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("locationscanningreceiver.py -v <validator> -s <secret>")
            sys.exit()
        elif opt in ("-v", "--validator"):
            validator = arg
        elif opt in ("-s", "--secret"):
            secret = arg

    print("validator: " + validator)
    print("secret: " + secret)


if __name__ == "__main__":
    main(sys.argv[1:])
    app.run()