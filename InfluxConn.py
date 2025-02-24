import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_influx_data(start_range="-30m", filters=[{"sensor_type": "temperature"}, {"room_id": "1.233"}]):
    org = os.getenv("org")
    token = os.getenv("token")
    url = os.getenv("url")

    client = influxdb_client.InfluxDBClient(
       url=url,
       token=token,
       org=org
    )

    #Construct filters
    filter_string = ""
    for query_filter in filters:
        filterlist(query_filter)[0])

    query_api = client.query_api()
    query = ('from(bucket:"db")\
             |> range(start: ' + start_range + ')\
             |> filter(fn: (r) => r["sensor_type"] == "temperature")\
             |> filter(fn: (r) => r["room_id"] == "1.233")')
    result = query_api.query(org=org, query=query)
    results = []
    for table in result:
      for record in table.records:
        if record.get_field() != "unit":
            results.append((record.get_time().strftime("%d/%m/%Y, %H:%M:%S"), record.get_field(), record.get_value()))
        else:
          results.append(("time", record.get_field(), record.get_value()))
      print(results)
      results = []


get_influx_data();