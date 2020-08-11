import requests
import json


def get_permissions(consumer_id, module):
    params = (
        ('package', module),
        ('consumer_id', consumer_id)
    )
    response = requests.get('https://aheadworks@dist.aheadworks.com/api/v1/permissions', headers=headers, params=params)
    e = "message"
    if not e in response.text:
        return response.text
    else:
        return get_permissions(consumer_id, module)

with open('./composer.json') as f:
    composer = json.load(f)
core_module = composer['name']
modules = list()
for module in composer['suggests']:
    if module.find(core_module) != -1:
        modules.append(module)

headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer HDIEhdijendejded',
}

response_core_package = requests.get('https://aheadworks@dist.aheadworks.com/api/v1/packages?name=' + core_module,
                                     headers=headers)
response_permissions = requests.get('https://aheadworks@dist.aheadworks.com/api/v1/permissions?package=' + core_module,
                                    headers=headers)
core_package = json.loads(response_core_package.text)[0]['id']
permissions = json.loads(response_permissions.text)
print(core_package)
consumer_ids = list()
for p in permissions:
    if p['package_id'] == core_package:
        consumer_ids.append(p["consumer_id"])
suggest_packages_ids = list()
print(consumer_ids)
for m in modules:
    print(m)
    params = (
        ('name', m),
    )
    module = requests.get('https://aheadworks@dist.aheadworks.com/api/v1/packages', headers=headers, params=params)
    suggest_packages_ids.append(json.loads(module.text)[0]['id'])
print(suggest_packages_ids)
consumer_id: int
for consumer_id in consumer_ids:
    for module in modules:
        permissions = (get_permissions(consumer_id, module))
        if not permissions == '[]':
            print(permissions)
        else:
            version = '*'
            r = requests.post('https://aheadworks@dist.aheadworks.com/api/v1/permissions', headers=headers, params=params, json={'consumer_id': consumer_id, 'package': module, 'version': version})
            if "message" in r.text:
               while not ("message" in r.text):
                   r = requests.post('https://aheadworks@dist.aheadworks.com/api/v1/permissions', headers=headers, params=params, json={'consumer_id': consumer_id, 'package': module, 'version': version})
            print(r.request)
            print(r.text)
            print(r.status_code)