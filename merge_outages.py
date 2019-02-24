import json

country_list = []
json_filenames = []
with open('./africa_codes.txt', 'r') as codes_file:
    for code in codes_file.readlines():
        country_list.append(code.strip())
        json_filenames.append('./africa/'+code.strip()+'.json')

output = {
    "meta": {
        "country": [],
        "start": "2014-01-01T00:00:00",
        "stop": "2019-02-23T12:42:25"
    },
    "isps": []
}

for filename in json_filenames:
    with open(filename, 'r') as json_file:
        meta_data = json.load(json_file)
        for isps in meta_data['isps']:
            isps['pct'] = float(isps['pct'])/126*10
        output['meta']['country'].append(meta_data['meta']['country'])
        output['isps'] += meta_data['isps']
    
print(len(output['isps']))
with open('africa_all_country.json', 'w') as output_file:
    output_file.write(json.dumps(output, indent=2))