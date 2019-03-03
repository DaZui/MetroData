

def generateStationID(line, station_sequence):
    return "{0}_{1}".format(line, station_sequence)

def addLine(line):
    visited_stations = {}
    line_id = line["id"] if "id" in line else line["Name"]

    genete["Lines"][line_id] = {
        "name": {
            "zh": line["Name"]
        },
        "color": line["Color"],
        "shortname": line["ShortName"] if "ShortName" in line else line["Name"]
    }
    if "Ring" in line:
        if line["Ring"] == 1:
            direction = ["ccw", "cw"]
        elif line["Ring"] == -1:
            direction = ["cw", "ccw"]
    else:
        last_stop_id = generateStationID(line_id, len(line["Stations"]))
        first_stop_id = generateStationID(line_id, 1)

        if "Single" in line:
            direction = [last_stop_id, ""]
        else:
            direction = [last_stop_id, first_stop_id]

    genete["Lines"][line_id]["direction"] = direction
    system = line["System"] if "System" in line else "Metro"
    genete["Systems"][system] = {
        "zh": system
    }
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
                "system": system
            }
        if i - 1 >= 0 and "Single" not in line:
            temp["neighbors"][generateStationID(line_id, stat_id - 1)] = {
                "type": "train",
                "direction": direction[1],
                "line": line_id,
                "system": system
            }
        if "Ring" in line:
            if i == num_of_stations - 1:
                temp["neighbors"][generateStationID(line_id, 1)] = {
                    "type": "train",
                    "direction": direction[0],
                    "line": line_id,
                    "system": system
                }

            if i == 0:
                temp["neighbors"][generateStationID(line_id, num_of_stations)] = {
                    "type": "train",
                    "line": line_id,
                    "direction": direction[1],
                    "system": system
                }
        station_name = stations[i]
        if station_name not in visited_stations:
            visited_stations[station_name] = []
        visited_stations[station_name].append(station_id)
        genete["Stations"][station_id] = temp