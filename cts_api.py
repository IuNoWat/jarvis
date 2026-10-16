import requests as r
import keys
import time

basic = r.auth.HTTPBasicAuth(username=keys.username,password=keys.password)

base_url = "https://api.cts-strasbourg.eu/v1/siri/2.0/stop-monitoring?MonitoringRef="

def get_visits(stop_code) :
    request_url = base_url +  stop_code
    print("Making request : "+request_url)
    response = r.get(request_url,auth=basic)
    as_json = response.json()
    vehicles = []
    list_of_visits = as_json["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
    for entry in list_of_visits :
        vehicles.append(entry["MonitoredVehicleJourney"])
    return vehicles

def get_info(vehicle) :
    #print(vehicle)
    absolute_time = time.strptime(vehicle["MonitoredCall"]["ExpectedArrivalTime"],"%Y-%m-%dT%H:%M:%S+02:00")
    as_epoch = time.mktime(absolute_time)

    to_return = {
        "line":vehicle["LineRef"],
        "type":vehicle["VehicleMode"],
        "direction":vehicle["DestinationName"],
        "expected":time.strftime("%H:%M",time.localtime(as_epoch)),
        "arrival_in":int((as_epoch-time.time())/60)
    }
    return to_return


test = get_visits("517")


for entry in test  :
    print(get_info(entry))
