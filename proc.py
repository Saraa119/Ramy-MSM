import json 

with open('data.json', 'r') as read_file:
    data = json.load(read_file)


# print(data['departments'][0]['Cardiology']['Equipment'][0]["name"])

for dep in data['departments']:   
    for dep_name in dep:
        for equip in dep[dep_name]['Equipment']:
            print(equip)