from zabbix_api import ZabbixAPI

## falls man mal wieder keine lust hat ein template zu exportieren und als xml zu importieren
## kann man so eine vermantschte sache machen wo ein dummy host erzeugt wird mit einem template 
## für eine existierende template group und in einer existierenden host group 
## und einem trigger für mehrere http checks die als web scenarios erzeugt werden 
## wenn der host schon existiert, dann wird das template gesetzt und nicht appended!
## ist das template neu, dann bekommt es auch die trigger - sonst failen alle drei requests mit exception weil schon existiert 

## die http checks werden in json form siehe unten als test daten definiert
## das script erzeugt alles was es braucht -> idempotent und für neusysteme geeignet 
## todo: wenn sich die daten ändern -> http test hinzu 
## dann muss der trigger neu erzeugt werden 
## löschen und neu machen? oder geht update eh gut? für beides testen 
## created by b.leenhoff Februar 2024 @home 
##
## importiert eine recht alte lib, die aber aktuell ist. nur die doku ist meh 
## pip install zabbix_api


ZABBIX_SERVER = 'http://192.168.50.106/zabbix'
USERNAME = 'Admin'
PASSWORD = 'zabbix'



new_template_for_host = 'Template with HTTP Tests 123'
template_group = 'Templates/random-checks'
new_or_updated_host_name = 'dummy023'
host_group_for_host = 'Virtual machines'


# Create a ZabbixAPI instance
##zapi = ZabbixAPI(server=ZABBIX_SERVER, path="", log_level=6)
zapi = ZabbixAPI(server=ZABBIX_SERVER)
zapi.login(USERNAME, PASSWORD)

##{"expandExpression": "extend", "triggerids": range(0, 100)}
## https://www.zabbix.com/documentation/current/en/manual/api/reference/trigger/create
## https://www.zabbix.com/documentation/6.4/en/manual/api/reference/trigger/object

def get_template_group_id(template_group_name):
    """Get the template group ID from the template group name."""
    template_groups = zapi.templategroup.get({"filter":{"name":template_group_name}})
    if template_groups:
        return template_groups[0]['groupid']
    else:
        raise ValueError(f"Template group '{template_group_name}' not found.")

    
def create_template(template_name, template_group_name):
    """Create a new template with the specified template group."""
    try:
        # Get the template group ID
        template_group_id = get_template_group_id(template_group_name)
        print("template group id: ", template_group_id)
        
        # Check if the template already exists
        existing_template_id = get_template_id(template_name)
        if existing_template_id:
            print(f"Template '{template_name}' already exists with ID: {existing_template_id}")
            return existing_template_id
        
        # Create a new template
        new_template = zapi.template.create({"host":template_name, "groups": {"groupid": template_group_id}})
        print(f"New template '{template_name}' created with ID: {new_template['templateids'][0]}")
        return new_template['templateids'][0]

    except Exception as e:
        print(f"Failed to create template: {e}")
        return None

def get_template_id(template_name):
    """Get the ID of a template by its name."""
    try:
        templates = zapi.template.get({"filter":{"host":template_name}})
        return templates[0]['templateid']
    except Exception as e:
        print(f"Failed to get template ID: {e}")
        return None
    
# the function wil return the id of the template if it exists or create it if it does not exist
template_id = create_template(new_template_for_host, template_group)
#template_group_id = get_template_group_id('bla')
##print("we came so far...", template_id)
#exit()
# Create HTTP tests as json data 
expression_parts=[]

httptests = [
    {
        'name': 'HTTP Test 1', 
        'hostid': template_id,
        'steps': [
            {
                'name': 'HTTP Step 1',
                'url': 'http://examplasdfsfge.com',  
                'status_codes': '200,301',
                'no': 1
            }
        ]
    },
    {
        'name': 'HTTP Test 2',
        'hostid': template_id,
        'steps': [
            {
                'name': 'HTTP Step 2',
                'url': 'http://example.org',
                'status_codes': '200,301',
                'no': 1
            }
        ]
    },
    {
        'name': 'HTTP Test 3', 
        'hostid': template_id,
        'steps': [
            {
                'name': 'HTTP Step 3',
                'url': 'http://google.com',
                'status_codes': '200,301',
                'no': 1
            }
        ]
    }
]

## create the http tests and prepare trigger expressions
for httptest in httptests:
    expression_parts.append(httptest['name'])
    try: 
        new_httptest = zapi.httptest.create(httptest)
        print(f"New HTTP test created with ID: {new_httptest['httptestids'][0]}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"HTTP test {httptest['name']}: already exists")
        else:
            print(f"Failed to create HTTP test: {e}")
    
###Create a trigger for the HTTP tests
    ###expression = "{Template with HTTP Tests:web.test.fail[HTTP Test 1].last()}=1 or {Template with HTTP Tests:web.test.fail[HTTP Test 2].last()}=1"
description = 'Web scenario "HTTP Test" failed: {ITEM.VALUE}'
expression = ""
for expression_part in expression_parts:
    sp = f"length(last(/{new_template_for_host}/web.test.error[{expression_part}]))>0 and last(/{new_template_for_host}/web.test.fail[{expression_part}])>0"
    expression += sp + ' or '
#print("expre: ", expression[0:-4])
## remove the last ' or '
expression = expression[0:-4]
## not used atm -> see desc / name -> is what we see in UI and at dashboard with zabbix putting the value 
opdata = 'Web scenario "Scenario" failed: {ITEM.VALUE}'
   
try:
    new_trigger = zapi.trigger.create({'description': description, 'expression': expression, 'priority': 3, 'manual_close': 1})
    print(f"New trigger created with ID: {new_trigger['triggerids'][0]}")
except Exception as e:
    if "already exists" in str(e):
        print("Trigger already exists")
        ## have id from the exception message 
        ## update trigger to keep problems and history in zabbix instead of del and create 
    else:
        print(f"Failed to create trigger: {e}")


### create the dummy host - http tests are run from the zabbix server 

def get_host_group_id(group_name):
    """Get the group ID from the group name."""
    groups = zapi.hostgroup.get({"filter": {'name': group_name}})
    if groups:
        return groups[0]['groupid']
    else:
        raise ValueError(f"Group '{group_name}' not found.")
        ## we can use this function with try n catch  

def manage_host_with_template(hostname, template_id, group_name):
    """Create or update a host with the specified template."""
    print("\nmanage host with template")
    try:
        # Get the hostgroup ID
        group_id = get_host_group_id(group_name)
        
        # Check if the host exists
        existing_hosts = zapi.host.get({"filter": {'host': hostname}})
        if existing_hosts:
            host_id = existing_hosts[0]['hostid']
            print(f"Host '{hostname}' already exists with ID: {host_id}")
            
            # Update the host to set the new template - should be updated so the template is added maybe <- feature req
            # only interesting if used for real hosts
            # for a dummy host we only ever set the one template 
            try:
                updated_host = zapi.host.update({"hostid": host_id, "templates": [{'templateid': template_id}]})
                print(f"Host '{hostname}' updated with template '{template_id}'.")
            except Exception as e:
                print(f"Failed to update host: {e}")
        else:
            # Create a new host if it does not exist
            new_host = zapi.host.create({"host": hostname,"groups": [{'groupid': group_id}],"templates": [{'templateid': template_id}]})
            print(f"New host '{hostname}' created with ID: {new_host['hostids'][0]}")

    except Exception as e:
        print(f"An error occurred: {e}")

### do all the things for the dummy host
manage_host_with_template(new_or_updated_host_name, get_template_id(new_template_for_host), host_group_for_host)

# Logout from Zabbix server - ka was in dem modul passiert 
##zapi.user.logout()