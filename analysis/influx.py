import influxdb_client
import pandas as pd
BUCKET = "bssr"
ORG = "BSSR"
TOKEN = "K1h0Bk9xIbuJiihHAywIXFE_IKnpO_81NWaiRFLCokXC5PSUMDPwwIJQmR7-bnBKfCejTS_gCy-A8YfmIAyeHQ=="
URL = "http://localhost:8086"


client = influxdb_client.InfluxDBClient(
   url=URL,
   token=TOKEN,
   org=ORG
)


query_api = client.query_api()

query1 = ' from(bucket: "bssr") \
  |> range(start: 2023-10-12 03:48:00, stop: 2023-10-12 06:48:00) \
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer") \
  |> filter(fn: (r) => r["_field"] == "target_power") \
  |> aggregateWindow(every: 100ms, fn: mean, createEmpty: false) \
  |> yield(name: "mean")  \
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \
  |> keep(columns: ["_time", "target_power"])'

query2 = ' from(bucket: "bssr") \
  |> range(start: -8h) \
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer") \
  |> filter(fn: (r) => r["_field"] == "car_speed") \
  |> aggregateWindow(every: 100ms, fn: mean, createEmpty: false) \
  |> yield(name: "mean")  \
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \
  |> keep(columns: ["_time", "car_speed"])'


query3 = ' from(bucket: "bssr") \
  |> range(start: 2023-10-12 03:48:00, stop: 2023-10-12 06:48:00) \
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer") \
  |> filter(fn: (r) => r["_field"] == "MCMB") \
  |> filter(fn: (r) => r["_topic"] == "bus_metrics/voltage/MCMB"  \
  |> aggregateWindow(every: 100ms, fn: mean, createEmpty: false) \
  |> yield(name: "mean")  \
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \
'

query3 = ' from(bucket: "bssr") \
  |> range(start: -8h) \
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer") \
  |> filter(fn: (r) => r["_field"] == "car_speed") \
  |> aggregateWindow(every: 100ms, fn: mean, createEmpty: false) \
  |> yield(name: "mean")  \
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \
  |> keep(columns: ["_time", ""])'

#result = query_api.query(org=ORG, query=query)
result1 = query_api.query_data_frame(query1)
result2 = query_api.query_data_frame(query2)
df = result1[1].merge(result2[1])
df = df.drop(columns=["result", "table"])

df.to_csv("kai.csv")
