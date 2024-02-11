from zabbix_api import ZabbixAPI

## falls man mal wieder keine lust hat ein template zu exportieren und als xml zu importieren
## kann man so eine vermantschte sache machen wo ein dummy host erzeugt wird mit einem template 
## für eine existierende template group und in einer existierenden host group 
## und einem trigger für mehrere http checks die als web scenarios erzeugt werden 
## wenn der host schon existiert, dann wird das template gesetzt und nicht appended!
## ist das template neu, dann bekommt es auch die trigger - sonst failen alle drei requests mit exception weil schon existiert 



# Replace with your Zabbix server URL, username, and password
# Replace with your Zabbix server URL, username, and password
ZABBIX_SERVER = 'http://192.168.50.106/zabbix'
USERNAME = 'Admin'
PASSWORD = 'zabbix'



new_template_for_host = 'Template with HTTP Tests 8'
template_group = 'Templates/random-checks'
new_or_updated_host_name = 'dummy007'
host_group_for_host = 'Virtual machines'


# Create a ZabbixAPI instance
##zapi = ZabbixAPI(server=ZABBIX_SERVER, path="", log_level=6)
zapi = ZabbixAPI(server=ZABBIX_SERVER)
zapi.login(USERNAME, PASSWORD)

##{"expandExpression": "extend", "triggerids": range(0, 100)}

def get_template_group_id(template_group_name):
    """Get the template group ID from the template group name."""
    ##{"filter":{"host":host_name}}
    template_groups = zapi.templategroup.get({"filter":{"name":template_group_name}})
    if template_groups:
        return template_groups[0]['groupid']
    else:
        raise ValueError(f"Template group '{template_group_name}' not found.")


# def create_template(template_name, template_group_name):
#     """Create a new template with the specified template group."""
#     try:
#         # Get the template group ID
#         template_group_id = get_template_group_id(template_group_name)
#         print("template group id: ", template_group_id)
        
#         # Create a new template
#         new_template = zapi.template.create({"host":template_name, "groups": {"groupid": template_group_id}})
#         print(f"New template '{template_name}' created with ID: {new_template['templateids'][0]}")
#         return new_template['templateids'][0]

#     except Exception as e:
#         print(f"Failed to create template: {e}")
#         return None
    
    ## garbage try 
# def create_template(template_name, template_group_name):
#     """Create a new template with the specified template group."""
#     try:
#         # Get the template group ID
#         template_group_id = get_template_group_id(template_group_name)
#         print("template group id: ", template_group_id)
        
#         # Check if the template already exists
#         existing_templates = zapi.template.get(filter={'host': template_name})
#         if existing_templates:
#             # If the template exists, return its ID
#             template_id = existing_templates[0]['templateid']
#             print(f"Template '{template_name}' already exists with ID: {template_id}")
#             return template_id
        
#         # If the template does not exist, create a new one
#         new_template = zapi.template.create({
#             "host": template_name,
#             "groups": [{"groupid": template_group_id}]
#         })
#         print(f"New template '{template_name}' created with ID: {new_template['templateids'][0]}")
#         return new_template['templateids'][0]

#     except Exception as e:
#         print(f"Failed to create template: {e}")
#         return None
    
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
        # Get template
        ##{"filter":{"host":template_name}}
        templates = zapi.template.get({"filter":{"host":template_name}})
        
        # If the template exists, return its ID
        if templates:
            return templates[0]['templateid']
        else:
            return None

    except Exception as e:
        print(f"Failed to get template ID: {e}")
        return None
    
# Example usage:
template_id = create_template(new_template_for_host, template_group)
#template_group_id = get_template_group_id('bla')
print("we came so far...", template_id)
#exit()
# Example: Create HTTP tests and associate them with the template
try:
    httptests = [
        {
            'name': 'HTTP Test 1',
            'hostid': template_id,
            'steps': [
                {
                    'name': 'HTTP Step 1',
                    'url': 'http://example.com',
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
        }
    ]

    for httptest in httptests:
        new_httptest = zapi.httptest.create(httptest)
        print(f"New HTTP test created with ID: {new_httptest['httptestids'][0]}")

except Exception as e:
    print(f"Failed to create HTTP tests: {e}")

###Example: Create a trigger for the HTTP tests
    ###expression = "{Template with HTTP Tests:web.test.fail[HTTP Test 1].last()}=1 or {Template with HTTP Tests:web.test.fail[HTTP Test 2].last()}=1"
description = "HTTP Test Failure 00"
expression = "last(/{}/web.test.rspcode[HTTP Test 1,HTTP Step 1])=1 and last(/{}/web.test.rspcode[HTTP Test 2,HTTP Step 2])=1".format(new_template_for_host, new_template_for_host)
   
try:
    new_trigger = zapi.trigger.create({'description': description, 'expression': expression})
    print(f"New trigger created with ID: {new_trigger['triggerids'][0]}")
except Exception as e:
    print(f"Failed to create trigger: {e}")


##{"filter":{"host":template_name}}

def get_host_group_id(group_name):
    """Get the group ID from the group name."""
    groups = zapi.hostgroup.get({"filter": {'name': group_name}})
    if groups:
        return groups[0]['groupid']
    else:
        raise ValueError(f"Group '{group_name}' not found.")

def manage_host_with_template(hostname, template_id, group_name):
    """Create or update a host with the specified template."""
    print("manage host with template bla\n")
    try:
        # Get the hostgroup ID
        group_id = get_host_group_id(group_name)
        
        # Check if the host exists
        existing_hosts = zapi.host.get({"filter": {'host': hostname}})
        print("last word: ", existing_hosts)
        if existing_hosts:
            host_id = existing_hosts[0]['hostid']
            print(f"Host '{hostname}' already exists with ID: {host_id}")
            
            # Update the host to include the template

            ## sowohl updates als auch create sind noch falsch 
            try:
                updated_host = zapi.host.update({"hostid": host_id, "templates": [{'templateid': template_id}]})
                print(f"Host '{hostname}' updated with template.")
            except Exception as e:
                print(f"Failed to update host: {e}")
        else:
            # Create a new host if it does not exist
            print("we are here arent we?")
            new_host = zapi.host.create({"host": hostname,"groups": [{'groupid': group_id}],"templates": [{'templateid': template_id}]})
            print(f"New host '{hostname}' created with ID: {new_host['hostids'][0]}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
manage_host_with_template(new_or_updated_host_name, get_template_id(new_template_for_host), host_group_for_host)

# Logout from Zabbix server - ka was in dem modul passiert 
##zapi.user.logout()