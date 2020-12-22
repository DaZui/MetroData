import json
import os

for i in os.listdir("old_data"):
    location, _ = i.split("_")
    with open("old_data/" + i, encoding="utf-8") as w:
        origin = json.load(w)
    genete = {"stations": {}, "lines": {}, "systems": {}}
    if "attentions" in origin:
        genete["attentions"] = origin["attentions"]
    visited_stations = {}

    def generateStationID(line, station_sequence):
        return "{0}_{1}".format(line, station_sequence)

    for line in origin["lines"]:
        if "id" in line:
            line_id = line["id"]
        elif "code" in line:
            line_id = line["code"]
        else:
            line_id = line["name"]

        while line_id in genete["lines"]:
            line_id = line_id + "_"

        genete["lines"][line_id] = {
            "name": {
                "zh": line["name"]
            },
            "color": line["color"],
            "system": line["system"],
            "type": line.get("type", ""),
            "code": line.get("code", line["name"]),
        }

        direction = ["ccw", "cw"][::line["ring"]] if "ring" in line else [
            generateStationID(line_id, len(line["stations"])),
            "" if "single" in line else generateStationID(line_id, 1)
        ]

        genete["lines"][line_id]["direction"] = direction
        system = line["system"] if "system" in line else "地铁"
        genete["systems"][system] = {"zh": system}
        stations = line["stations"]
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
            if i - 1 >= 0 and "single" not in line:
                temp["neighbors"][generateStationID(line_id, stat_id - 1)] = {
                    "type": "train",
                    "direction": direction[1],
                    "line": line_id,
                    "system": system,
                }
            if "ring" in line:
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
            genete["stations"][station_id] = temp
    for station in visited_stations:
        for station1_id in visited_stations[station]:
            for station2_id in visited_stations[station]:
                if station1_id == station2_id:
                    continue
                station_name = genete["stations"][station1_id]["name"]["zh"]
                line1_name, line2_name = map(
                    lambda x: genete["lines"][x.split("_")[0]]["name"]["zh"],
                    (station1_id, station2_id),
                )
                if "virtualTransfers" in origin and (
                    [station_name, line1_name, line2_name
                     ] in origin["virtualTransfers"]
                        or [station_name, line2_name, line1_name
                            ] in origin["virtualTransfers"]):
                    genete["stations"][station1_id]["neighbors"][
                        station2_id] = {
                            "type": "walk-out"
                    }
                elif (genete["stations"][station1_id]["system"] !=
                      genete["stations"][station2_id]["system"]):
                    genete["stations"][station1_id]["neighbors"][
                        station2_id] = {
                            "type": "walk-transfer"
                    }
                else:
                    genete["stations"][station1_id]["neighbors"][
                        station2_id] = {
                            "type": "walk-in"
                    }
    if "connections" in origin:
        for p in origin["connections"]:
            if len(p) == 4:
                station1, station2, connectiontype, system = p
                station1_ids = []
                station2_ids = []
                for station_id in genete["stations"]:
                    if (genete["stations"][station_id]["name"]["zh"]
                            == station1
                            and genete["stations"][station_id]["system"]
                            == system):
                        station1_ids.append(station_id)

                    if (genete["stations"][station_id]["name"]["zh"]
                            == station2
                            and genete["stations"][station_id]["system"]
                            == system):
                        station2_ids.append(station_id)
            if len(p) == 5:
                station1, station2, connectiontype, system1, system2 = p
                station1_ids, station2_ids = [], []
                for station_id in genete["stations"]:
                    if (genete["stations"][station_id]["name"]["zh"]
                            == station1
                            and genete["stations"][station_id]["system"]
                            in system1):
                        station1_ids.append(station_id)

                    if (genete["stations"][station_id]["name"]["zh"]
                            == station2
                            and genete["stations"][station_id]["system"]
                            in system2):
                        station2_ids.append(station_id)

            for station1_id in station1_ids:
                for station2_id in station2_ids:
                    genete["stations"][station1_id]["neighbors"][
                        station2_id] = {
                            "type": connectiontype
                    }
                    genete["stations"][station2_id]["neighbors"][
                        station1_id] = {
                            "type": connectiontype
                    }

    with open("data/{0}.json".format(location), "w", encoding="utf-8") as w:
        json.dump(genete, w, indent=4, ensure_ascii=False)
