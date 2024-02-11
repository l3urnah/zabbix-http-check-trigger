from zabbix_api import ZabbixAPI

# Replace with your Zabbix server URL, username, and password
ZABBIX_SERVER = 'http://192.168.50.106/zabbix'
USERNAME = 'Admin'
PASSWORD = 'zabbix'

# Create a ZabbixAPI instance
zapi = ZabbixAPI(server=ZABBIX_SERVER) ##, path="", log_level=6
zapi.login(USERNAME, PASSWORD)

host_name="dummy00"

description='Used disk space on $1 in %' 
key='vfs.fs.size[/,pused]'

host=zapi.host.get({"filter":{"host":host_name}})
hostid=host[0]['hostid']
print(host)
host=zapi.host.get({"output": ["hostid"], "filter":{"host":host_name}})
print(host)
hostid=host[0]['hostid']
#zapi.item.create({ 'hostid' : (hostid),'description' : (description),'key_' : key })
host=zapi.host.get({"output": ["name"], "selectParentTemplates": ["templateid","name"],"hostids": hostid})
print(host)
host=zapi.host.get({"output": ["hostid"], "selectParentTemplates": ["templateid","name"],"filter":{"host":host_name}, "selectHostGroups": "extend"})
print(host)