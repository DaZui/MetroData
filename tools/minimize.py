import json
import os

for i in os.listdir('data'):
    c = json.load(open('data//' + i, encoding="utf-8"))
    json.dump(c, open('data//' + i, "w"))