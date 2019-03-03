import json
lang = "zh"

cpp = json.load(open("data/上海.json", encoding="utf-8"))
new_line_id = input("新线的唯一识别号：")
while new_line_id in cpp["Lines"]:
    new_line_id = input("已经存在，重新输入：")
print("新线的唯一识别号：{0}".format(new_line_id))
line = {
    "color": input("新线的颜色："),
    "direction": [
    ],
    "name": {
        "zh": input("新线的名称：")
    },
    "shortname": input("新线的代号：")
}

stations_list = input("新线的站点列表，以“ - ”分隔：")
stations_list = stations_list.split(" - ")
line["stations_list"] = stations_list
json.dump(line, open(new_line_id+".json", "w", encoding="utf-8"),
          ensure_ascii=False, sort_keys=True, indent=4)
