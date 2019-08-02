from __future__ import print_function
import sys
import os
import json
import pandas as pd
try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib

from functools import singledispatch

cur_dir = os.path.dirname(__file__)

routes = pd.read_csv(cur_dir + '/gtfs/routes.txt')
trips = pd.read_csv(cur_dir + '/gtfs/trips.txt')
shapes = pd.read_csv(cur_dir + '/gtfs/shapes.txt')
stop_times = pd.read_csv(cur_dir + '/gtfs/stop_times.txt')
stops = pd.read_csv(cur_dir + '/gtfs/stops.txt')
stop_times = pd.merge(stop_times, stops.loc[:,['stop_id', 'stop_lat', 'stop_lon']], on='stop_id')

def get_route_info(LineRef):

	route_id = LineRef.upper()

	result = {}
	result['route'] = routes.loc[routes.route_id == route_id,:].squeeze().to_dict()

	#Get the first trip for each direction (not perfect but works)
	trip_list = []
	trip_list.append(trips.loc[(trips.route_id == route_id) & (trips.direction_id == 0), :].head(1).squeeze().to_dict())
	trip_list.append(trips.loc[(trips.route_id == route_id) & (trips.direction_id == 1), :].head(1).squeeze().to_dict())

	result['trips'] = trip_list

	result['shapes'] = []
		
	#Get shapes and stops for each trip/direction
	for idx, trip in enumerate(trip_list):

		shape = {}
		shape['shape_id'] = trip['shape_id']
		shape['shape_points'] = shapes.loc[shapes.shape_id == trip['shape_id'], ['shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence']].to_dict('records')

		result['trips'][idx]['shape'] = shape

		result['trips'][idx]['stops'] = stop_times.loc[stop_times.trip_id == trip['trip_id'], stop_times.columns[1:]].to_dict('records')

	return result

def get_bus_locations(key, LineRef):

	#API version
	version = "2"

	#Set API endpoint
	url = "https://bustime.mta.info/api/siri/vehicle-monitoring.json?key={}&version={}&LineRef={}".format(key, version, LineRef.upper())

	#Read data
	response = urllib.urlopen(url)
	data = response.read().decode("utf-8")
	dataDict = json.loads(data)

	#Check for API errors
	if "ErrorCondition" in dataDict["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][0].keys():
		#Print error from API
		print("API ERROR: {}".format(dataDict["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][0]["ErrorCondition"]["Description"]))
		return []
	else:
		#Get buses
		return dataDict["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][0]["VehicleActivity"]


if __name__ == '__main__':

	#Check number of arguments
	if not len(sys.argv) == 3:
		print ("Invalid number of arguments. Run as: python show_bus_locations_pmb434.py MTA_API_KEY BUS_LINE")
		sys.exit()


	#Set parameters
	key = sys.argv[1]
	LineRef = sys.argv[2]

	buses = get_bus_locations(key, LineRef)

	#Print output
	print ("Bus Line: {}".format(LineRef))

	print ("Number of Active Buses: {}".format(len(buses)))

	for n in range(len(buses)):
		print("Bus {} is at latitude {} and longitude {}".format(
			n+1,
			buses[n]["MonitoredVehicleJourney"]["VehicleLocation"]["Latitude"],
			buses[n]["MonitoredVehicleJourney"]["VehicleLocation"]["Longitude"]
		))
