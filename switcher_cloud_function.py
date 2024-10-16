## This is the body of the cloud function
## Paste this into the code definition
## Be sure to set environment variables in cloud function definition:
## LOOKERSDK_BASE_URL, LOOKERSDK_CLIENT_ID, LOOKERSDK_CLIENT_SECRET, AUTHENTICATION_SECRET 
## Also be sure to add requirements.txt to the cloud function


import functions_framework
from flask import Response
import os, json
from typing import Union

import looker_sdk
from looker_sdk import models40 as mdls


## Init Looker SDK
LOOKERSDK_BASE_URL = os.environ.get("LOOKERSDK_BASE_URL")
LOOKERSDK_CLIENT_ID = os.environ.get("LOOKERSDK_CLIENT_ID")
LOOKERSDK_CLIENT_SECRET = os.environ.get("LOOKERSDK_CLIENT_SECRET")

contents = """
[Looker]
base_url = {}
client_id = {}
client_secret = {}
verify_ssl = True
""".format(LOOKERSDK_BASE_URL, LOOKERSDK_CLIENT_ID, LOOKERSDK_CLIENT_SECRET)

with open ("api.ini", "w") as f:
  f.write(contents)

sdk = looker_sdk.init40()


## Mapping
mapping_config = { # contains mappings between references in this script and properties Looker sends through data action
    "DB_NAME_FIELD": "switcher_database_name",
    "DB_WH_FIELD": "switcher_database_wh",
    "SECRET_FIELD": "customer_switcher_authentication_secret",
    "USER_ID_FIELD": "user_id"
}


@functions_framework.http
def main(request) -> Response:
    ''' This is an example of the json payload
        {
            "type": "cell",
            "attachment": null,
            "scheduled_plan": null,
            "data": {
                "database_wh": "db_wh_3",
                "customer_switcher_authentication_secret": "abcddAg",
                "value": "1",
                "rendered": "1",
                "database_name": "transactions"
            },
             "form_params": {}
        }
    '''

    try:   
        ## Get Payload
        request_data = request.get_json()['data']
        request_data_keys = request_data.keys()

        ## Authenticate
        if mapping_config['SECRET_FIELD'] not in request_data_keys:
            print('Request malformed.' + mapping_config['SECRET_FIELD'] + ' key is missing')
            return Response(response = 'UNAUTHORIZED', status = 401)
        
        authentication_secret = request_data[mapping_config['SECRET_FIELD']]
        if authentication_secret != os.environ.get("AUTHENTICATION_SECRET"):
            print(mapping_config['SECRET_FIELD'] + ' was sent with an incorrect value (' + authentication_secret + ')')
            return Response(response = 'UNAUTHORIZED', status = 401)
        

        ## Handle DB_WH_FIELD
        if mapping_config['DB_WH_FIELD'] not in request_data_keys:
            raise Exception(mapping_config['DB_WH_FIELD'] + ' key is missing')
        database_wh = request_data[mapping_config['DB_WH_FIELD']]

        ## Handle DB_NAME_FIELD
        if mapping_config['DB_NAME_FIELD'] not in request_data_keys:
            raise Exception(mapping_config['DB_NAME_FIELD'] + ' key is missing')
        database_name = request_data[mapping_config['DB_NAME_FIELD']]

        ## Handle USER_ID_FIELD
        if mapping_config['USER_ID_FIELD'] not in request_data_keys:
            raise Exception(mapping_config['USER_ID_FIELD'] + ' key is missing')
        user_id = str(request_data[mapping_config['USER_ID_FIELD']])


        ## Handle User Attributes
        attributes = sdk.all_user_attributes()

        id_database_wh_attribute = get_user_attribute_id(attributes, 'DB_WH_FIELD')
        if id_database_wh_attribute is None:
            raise Exception(mapping_config['DB_WH_FIELD'] + ' attribute was not found in Looker ' + LOOKERSDK_BASE_URL )
        
        id_database_name_attribute = get_user_attribute_id(attributes, 'DB_NAME_FIELD')
        if id_database_name_attribute is None:
            raise Exception(mapping_config['DB_NAME_FIELD'] + ' attribute was not found in Looker ' + LOOKERSDK_BASE_URL )


        update_user_attribute(user_id, id_database_wh_attribute, database_wh)
        update_user_attribute(user_id, id_database_name_attribute, database_name)

        response = {
            "looker": {
                "success": True,
                "refresh_query": True
            }
        }
        return Response(json.dumps(response), status = 200, content_type='application/json')

    except Exception as e:
        print("ERROR ", e)

        response = {
            "looker": {
                "success": False,
                "validation_errors": {
                    "body": "AN ERROR OCCURED " + e.args[0]
                }
            }
        }
        # return Response(response = 'AN ERROR OCCURED ' + e.args[0], status = 400)
        return Response(json.dumps(response), status = 400)



def get_user_attribute_id(attributes: list, attribute_name: str) -> Union[int, None]:

    id = None
    for attribute in attributes:
        if attribute.name == mapping_config[attribute_name]:
            id = attribute.id
            break

    return id


def update_user_attribute(user_id: str, user_attribute_id: str, value: str) -> None:
    response = sdk.set_user_attribute_user_value(
        user_id=user_id,
        user_attribute_id=user_attribute_id,
        body=mdls.WriteUserAttributeWithValue(
            value=value
        )
    )

    if response.value != value:
        raise Exception('Failed to update user attribute id '+user_attribute_id+' for user id '+user_id+' with value '+value)
