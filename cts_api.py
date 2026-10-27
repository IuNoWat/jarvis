import requests as r
import time

import keys

basic = r.auth.HTTPBasicAuth(username=keys.username,password=keys.password)

base_url = "https://api.cts-strasbourg.eu/v1/siri/2.0/stop-monitoring?MonitoringRef="

def get_visits(stop_code:str) :
    """
    Returns all "vehicles" coming to a stop
    stop_code can be a LogicalStopCode (all directions of the stop) or a StopCode (only one physical stop)
    There is a list of StopCode in stop_codes.txt 
    """
    request_url = base_url +  stop_code
    print("Making request : "+request_url)

    response = r.get(request_url,auth=basic)
    print(f"Response received with code {response.status_code}")

    as_json = response.json()
    list_of_visits = as_json["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]

    vehicles = []
    for entry in list_of_visits :
        vehicles.append(entry["MonitoredVehicleJourney"])

    return vehicles



def get_info(vehicle) :
    arrival_time = time.strptime(vehicle["MonitoredCall"]["ExpectedArrivalTime"][:19],"%Y-%m-%dT%H:%M:%S")
    arrival_time_as_epoch = time.mktime(arrival_time)

    to_return = {
        "line":vehicle["LineRef"],
        "type":vehicle["VehicleMode"],
        "direction":vehicle["DestinationName"],
        "expected":time.strftime("%H:%M",time.localtime(arrival_time_as_epoch)),
        "arrival_in":int((arrival_time_as_epoch-time.time())/60)
    }

    return to_return



