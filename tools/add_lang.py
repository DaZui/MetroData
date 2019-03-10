import json
lang = "en"

cpp = json.load(open("上海.json", encoding="utf-8"))
try:
    cache = json.load(open("cache.json", encoding="utf-8"))
except:
    cache = {}
for line_name in cpp["Lines"]:
    line = cpp["Lines"][line_name]
    if lang not in line['name']:
        print("當前無", line, line['name']['zh'])
        if line['name']['zh'] in cache:
            print("緩存:", cache[line['name']['zh']])
            cpp["Lines"][line_name]['name'][lang] = cache[line['name']['zh']]
        else:
            c = input("新：")
            cpp["Lines"][line_name]['name'][lang] = c
            cache[line['name']['zh']] = c
json.dump(cache, open("cache.json", "w", encoding="utf-8"),
              indent=4, ensure_ascii=False, sort_keys=True)


for system_name in cpp["Systems"]:
    line = cpp["Systems"][system_name]
    if lang not in line:
        print("當前無")
        if line['zh'] in cache:
            print("緩存:", cache[line['zh']])
            cpp["Systems"][system_name][lang] = cache[line['zh']]
        else:
            c = input("新：")
            cpp["Systems"][system_name][lang] = c
            cache[line['zh']] = c
json.dump(cache, open("cache.json", "w", encoding="utf-8"),
              indent=4, ensure_ascii=False, sort_keys=True)
for station_name in cpp["Stations"]:
    line = cpp["Stations"][station_name]
    if lang not in line['name']:
        print("{0} 當前無".format(line['name']['zh']))
        if line['name']['zh'] in cache:
            print("緩存:", cache[line['name']['zh']])
            cpp["Stations"][station_name]['name'][lang] = cache[line['name']['zh']]
        else:
            c = input("新：")
            cpp["Stations"][station_name]['name'][lang] = c
            cache[line['name']['zh']] = c
    json.dump(cpp, open("香港.json", "w", encoding="utf-8"),
              indent=4, ensure_ascii=False, sort_keys=True)
json.dump(cache, open("cache.json", "w", encoding="utf-8"),
              indent=4, ensure_ascii=False, sort_keys=True)
