import json
import os

for i in os.listdir("old_data"):
    location, _ = i.split("_")
    with open("old_data/" + i, encoding="utf-8") as w:
        origin = json.load(w)
    genete = {"Stations": {}, "Lines": {}, "Systems": {}}
    if "Attention" in origin:
        genete["Attention"] = origin["Attention"]
    if "Long-Distance" in origin:
        genete["Long-Distance"] = origin["Long-Distance"]
    visited_stations = {}

    def generateStationID(line, station_sequence):
        return "{0}_{1}".format(line, station_sequence)

    for line in origin["Lines"]:
        if "id" in line:
            line_id = line["id"]
        elif "ShortName" in line:
            line_id = line["ShortName"]
        else:
            line_id = line["Name"]

        while line_id in genete["Lines"]:
            line_id = line_id + "_"

        genete["Lines"][line_id] = {
            "name": {
                "zh": line["Name"]
            },
            "color": line["Color"],
            "system": line["System"],
            "type": line.get("Type", ""),
            "shortname": line.get("ShortName", line["Name"]),
        }

        direction = ["ccw", "cw"][::line["Ring"]] if "Ring" in line else [
            generateStationID(line_id, len(line["Stations"])),
            "" if "Single" in line else generateStationID(line_id, 1)
        ]

        genete["Lines"][line_id]["direction"] = direction
        system = line["System"] if "System" in line else "地铁"
        genete["Systems"][system] = {"zh": system}
        stations = line["Stations"]
        num_of_stations = len(stations)
        for i in range(num_of_stations):
            stat_id = i + 1
            station_id = generateStationID(line_id, stat_id)
            temp = {}
            temp["name"] = {"zh": stations[i]}
            temp["line"] = line_id
            temp["system"] = system
            temp["neighbors"] = {}
            if i + 1 < num_of_stations:
                temp["neighbors"][generateStationID(line_id, stat_id + 1)] = {
                    "type": "train",
                    "direction": direction[0],
                    "line": line_id,
                    "system": system,
                }
            if i - 1 >= 0 and "Single" not in line:
                temp["neighbors"][generateStationID(line_id, stat_id - 1)] = {
                    "type": "train",
                    "direction": direction[1],
                    "line": line_id,
                    "system": system,
                }
            if "Ring" in line:
                if i == num_of_stations - 1:
                    temp["neighbors"][generateStationID(line_id, 1)] = {
                        "type": "train",
                        "direction": direction[0],
                        "line": line_id,
                        "system": system,
                    }

                if i == 0:
                    temp["neighbors"][generateStationID(
                        line_id, num_of_stations)] = {
                            "type": "train",
                            "line": line_id,
                            "direction": direction[1],
                            "system": system,
                    }
            station_name = stations[i]
            if station_name not in visited_stations:
                visited_stations[station_name] = []
            visited_stations[station_name].append(station_id)
            genete["Stations"][station_id] = temp
    for station in visited_stations:
        for station1_id in visited_stations[station]:
            for station2_id in visited_stations[station]:
                if station1_id == station2_id:
                    continue
                station_name = genete["Stations"][station1_id]["name"]["zh"]
                line1_name, line2_name = map(
                    lambda x: genete["Lines"][x.split("_")[0]]["name"]["zh"],
                    (station1_id, station2_id),
                )
                if "VirtualTransfers" in origin and (
                    [station_name, line1_name, line2_name
                     ] in origin["VirtualTransfers"]
                        or [station_name, line2_name, line1_name
                            ] in origin["VirtualTransfers"]):
                    genete["Stations"][station1_id]["neighbors"][
                        station2_id] = {
                            "type": "walk-out"
                    }
                elif (genete["Stations"][station1_id]["system"] !=
                      genete["Stations"][station2_id]["system"]):
                    genete["Stations"][station1_id]["neighbors"][
                        station2_id] = {
                            "type": "walk-transfer"
                    }
                else:
                    genete["Stations"][station1_id]["neighbors"][
                        station2_id] = {
                            "type": "walk-in"
                    }
    if "Connection" in origin:
        for p in origin["Connection"]:
            if len(p) == 4:
                station1, station2, connectiontype, system = p
                station1_ids = []
                station2_ids = []
                for station_id in genete["Stations"]:
                    if (genete["Stations"][station_id]["name"]["zh"]
                            == station1
                            and genete["Stations"][station_id]["system"]
                            == system):
                        station1_ids.append(station_id)

                    if (genete["Stations"][station_id]["name"]["zh"]
                            == station2
                            and genete["Stations"][station_id]["system"]
                            == system):
                        station2_ids.append(station_id)
            if len(p) == 5:
                station1, station2, connectiontype, system1, system2 = p
                station1_ids, station2_ids = [], []
                for station_id in genete["Stations"]:
                    if (genete["Stations"][station_id]["name"]["zh"]
                            == station1
                            and genete["Stations"][station_id]["system"]
                            in system1):
                        station1_ids.append(station_id)

                    if (genete["Stations"][station_id]["name"]["zh"]
                            == station2
                            and genete["Stations"][station_id]["system"]
                            in system2):
                        station2_ids.append(station_id)

            for station1_id in station1_ids:
                for station2_id in station2_ids:
                    genete["Stations"][station1_id]["neighbors"][
                        station2_id] = {
                            "type": connectiontype
                    }
                    genete["Stations"][station2_id]["neighbors"][
                        station1_id] = {
                            "type": connectiontype
                    }

    with open("data/{0}.json".format(location), "w", encoding="utf-8") as w:
        json.dump(genete, w, indent=4, ensure_ascii=False)
