import json
import os


class City:
    def __init__(self, filename):
        self.city = filename.split(".")[0]
        self.used_line_id = set()
        self.source_file_path = "old_data/{}.json".format(self.city)
        self.target_file_path = "data/{}.json".format(self.city)
        self.attentions = self.content.get("attentions", [])
        self.systems = sorted(
            list({line.get("system", "地铁") for line in self.content["lines"]}))

    @property
    def content(self):
        with open(self.source_file_path, encoding="utf-8") as w:
            return json.load(w)

    class Line:
        def __init__(self, line_data):
            self.data = line_data
            self.code = self.data['code']
            self.color = self.data['color']
            self.stations = self.data['stations']
            self.system = self.data.get("system", "地铁")
            self.name = self.data.get("name", self.code + " 号线")
            self.ring = self.data.get('ring', False)
            self.single = self.data.get('single', False)
            self.id = "{}/{}/{}/{}".format(
                self.system,
                self.data.get("id", self.code),
                self.stations[0],
                self.stations[-1]
            )

        def station_id(self, station_idx):
            return "{}_{}".format(self.id, station_idx)

        @property
        def directions(self):
            if self.ring:
                return {
                    "逆": ["ccw", "cw"],
                    "顺": ["cw", "ccw"]
                }[self.ring]
            direction = [self.station_id(len(self.stations) - 1)]
            if not self.single:
                direction.append(self.station_id(0))
            return direction

        @property
        def output_json(self):
            return {
                "code": self.code,
                "color": self.color,
                "name": self.name,
                "system": self.system,
                "direction": self.directions
            }

        def direction_indicator(self, idx):
            return {
                "type": "train",
                "direction": self.directions[idx],
                "line": self.id,
                "system": self.system,
            }

        def neighbors_of_a_station(self, i):
            neighbors = {}
            if i + 1 < len(self.stations):
                neighbors[self.station_id(i + 1)] = self.direction_indicator(0)
            if i - 1 >= 0 and not self.single:
                neighbors[self.station_id(i - 1)] = self.direction_indicator(1)
            if self.ring and i == len(self.stations) - 1:
                neighbors[self.station_id(0)] = self.direction_indicator(0)
            if self.ring and i == 0:
                neighbors[self.station_id(
                    len(self.stations) - 1)] = self.direction_indicator(1)

            return {
                "name": self.stations[i],
                "line": self.id,
                "system": self.system,
                "neighbors": neighbors
            }

        @property
        def output_stations(self):
            return {
                self.station_id(i): self.neighbors_of_a_station(i)
                for i, name in enumerate(self.stations)
            }

    @property
    def lines(self):
        return [self.Line(x) for x in self.content["lines"]]

    @property
    def virtualTransfers(self):
        return self.content.get('virtualTransfers', [])

    @property
    def connections(self):
        u = []
        for p in self.content.get('connections', []):
            if len(p) == 4:
                station1, station2, connectiontype, system = p
                u.append([station1, station2, connectiontype, [system], [system]])
            elif len(p) == 5:
                u.append(p)
        return u

    @property
    def lines_output(self):
        return {line.id: line.output_json for line in self.lines}

    @property
    def all_stations(self):
        visited_stations = {}
        for line in self.lines:
            for i, name in enumerate(line.stations):
                visited_stations[name] = visited_stations.get(
                    name, []) + [line.station_id(i)]
        return visited_stations

    @property
    def stations_output(self):
        v = {}
        for line in self.lines:
            for key, val in line.output_stations.items():
                v[key] = val

        for name, ids in self.all_stations.items():
            if len(ids) < 2:
                continue

            for id1, id2 in [(a, b) for a in ids for b in ids if a < b]:
                def get_line_name(station_id):
                    line_id, station_idx = station_id.split("_")
                    return line_id

                line1 = get_line_name(id1)
                line2 = get_line_name(id2)

                if (
                    [name, line1, line2] in self.virtualTransfers or
                    [name, line2, line1] in self.virtualTransfers
                ):
                    transfer_type = "walk-out"
                elif v[id1]["system"] != v[id2]["system"]:
                    transfer_type = "walk-transfer"
                else:
                    transfer_type = "walk-in"

                _ = {"type": transfer_type}
                v[id1]["neighbors"][id2] = _
                v[id2]["neighbors"][id1] = _

        for p in self.connections:
            station1, station2, connectiontype, system1, system2 = p

            def f(a, b):
                return [
                    station_id for station_id, _ in v.items()
                    if _["name"] == a and _["system"] in b
                ]

            _ = {"type": connectiontype}
            for id1 in f(station1, system1):
                for id2 in f(station2, system2):
                    v[id1]["neighbors"][id2] = _
                    v[id2]["neighbors"][id1] = _
        return v

    @property
    def output_json(self):
        return {
            "attentions": self.attentions,
            "lines": self.lines_output,
            "stations": self.stations_output,
            "systems": self.systems
        }

    def output(self):
        with open(self.target_file_path, "w", encoding="utf-8") as w:
            json.dump(self.output_json, w, indent=4, ensure_ascii=False)


for location in os.listdir("old_data"):
    City(location).output()
