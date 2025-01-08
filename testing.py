import requests
import json 
import logging
import sys
import boto3
import socket
# create users
logging.basicConfig(filename="newfile.log",format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
aws_management_console = boto3.session.Session(profile_name= "default")
def create_user():
    url = "https://console.jumpcloud.com/api/v2/bulk/users"

    querystring = {"suppressEmail":"true"}

    payload = [
        {
            "attributes": [{"name":"EmployeeID","value":"0000"}],
            "email": "arle.trinada+dev@gmail.com",
            "firstname": "test1",
            "lastname": "veltris",
            "username": "test1"
        }
    ]
    headers = {
        "creation-source": "jumpcloud:bulk",
        "x-api-key": "jca_5EEH8u1ydMtu5hRVGBdHkD4E7EHEJFeUfP5A",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    user_job_iD = json.loads(response.text)
    if  user_job_iD:
        url = "https://console.jumpcloud.com/api/v2/bulk/users/{0}/results".format(user_job_iD['jobId'])

        querystring = {"limit":"10","skip":"0"}

        headers = {"x-api-key": "jca_5EEH8u1ydMtu5hRVGBdHkD4E7EHEJFeUfP5A"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        user_meta_data = json.loads(response.text)
        #print(user_meta_data)
        user_id = user_meta_data[0]['meta']['systemUser']['id']
        return user_id

# creating a new user_group 
def create_new_user_group():
    url = "https://console.jumpcloud.com/api/v2/usergroups"

    payload = {
        "attributes": {
            "sudo": {
                "enabled": True,
                "withoutPassword": True
            },
        },
        "email": "arle.trinada+user_group+1@gmail.com",
        "name": "test_group1"
    }
    headers = {
        "x-api-key": "jca_5EEH8u1ydMtu5hRVGBdHkD4E7EHEJFeUfP5A",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    group_data = json.loads(response.text)
    group_id = group_data['id']
    return group_id

# get exising user_group
def get_existing_groups():
    url = "https://console.jumpcloud.com/api/v2/usergroups"

    querystring = {"fields":"","filter":"","limit":"10","skip":"0","sort":""}

    headers = {"x-api-key": "jca_5EEH8u1ydMtu5hRVGBdHkD4E7EHEJFeUfP5A"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    exsiting_group = json.loads(response.text)
    existing_group_id = exsiting_group[0]['id']
    return existing_group_id

# add user to group 
def add_user_to_group(user_id,existing_group_id):
    url = "https://console.jumpcloud.com/api/v2/usergroups/{0}/members".format(existing_group_id)

    payload = {
        "id": user_id,
        "op": "add",
        "type": "user"
    }
    headers = {
        "x-api-key": "jca_5EEH8u1ydMtu5hRVGBdHkD4E7EHEJFeUfP5A",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)

## list the application 
def add_groups_application(group_id):
    url = "https://console.jumpcloud.com/api/v2/applications/"

    headers = {"x-api-key": "jca_5EEH8u1ydMtu5hRVGBdHkD4E7EHEJFeUfP5A"}

    response = requests.request("GET", url, headers=headers)

    app_data = json.loads(response.text)
    app_id = app_data[0]["_id"]

    # Add group to application 
    url = "https://console.jumpcloud.com/api/v2/applications/{0}/associations".format(app_id)

    payload = {
        "id": group_id,
        "op": "add",
        "attributes": {},
        "type": "user_group"
    }
    headers = {
        "x-api-key": "jca_5EEH8u1ydMtu5hRVGBdHkD4E7EHEJFeUfP5A",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response
def assing_policy():
    client = boto3.client('iam')
    response = client.attach_role_policy(PolicyArn='arn:aws:iam::478004422427:policy/test_policy', RoleName='sso_admin')
    params = {
        "RoleName": 'sso_admin' 
    }      
    while True:
        policies = client.list_attached_role_policies(**params)
        for p in policies["AttachedPolicies"]:
            logger.info(f"the policy attached are {p}")
        if not policies["IsTruncated"]:
            break
        else:
            params["Marker"] = policies["Marker"]
def create_ec2():
    ec2_console = aws_management_console.client(service_name="ec2")
    ec2_console = boto3.client("ec2")
    ec2_console.run_instances(ImageId = 'ami-01816d07b1128cd2d',MaxCount=1,MinCount=1,InstanceType='t2.micro')
    hostname = socket.gethostname()
    filters = [ {'Name': 'private-dns-name',
            'Values': [ hostname ]}
           ]

    response = ec2_console.describe_instances(Filters=filters)['ResponseMetadata']['HTTPStatusCode']
    print(f"the instance has been created with no error, Https code {response}")
   
def describe_instance():
    ec2_console = boto3.client("ec2")
    instance_id = ec2_console.describe_instances()['Reservations'][2]['Instances'][0]['InstanceId']
    instance_state = ec2_console.describe_instances()['Reservations'][2]['Instances'][0]['State']['Name']
    print(instance_id)
    print(instance_state)
    # terminating instacnes 
    response = ec2_console.terminate_instances(InstanceIds= [instance_id])
    logger.info(response)

def main():
    global user
    global create_group
    global user_add
    global app_add
    print("welcome to jumpcloud Onboarding!!!")
    value = int(input("please enter your requirements: \n 1. Create a new user and usergroup and add it to application \n 2. Create new user and add it old group \n"))
    if value == 1:
        user = create_user()
        logger.info(f"User has been created with userid {user}")
        create_group = create_new_user_group()
        logger.info(f"user group has been created with groupid {create_group}")
        user_add = add_user_to_group(user,create_group)
        logger.info(user_add)
        app_add = add_groups_application(create_group)
        logger.info(app_add)
        policy = assing_policy()
        logger.info(policy)

    elif value == 2:
        user = create_user()
        logger.info(f"User has been created with userid {user}")
        existing_group = get_existing_groups()
        logger.info(f"user group has been created with groupid {existing_group}")
        #logger.error(sys.stdout)
        user_add = add_user_to_group(user,existing_group)
        logger.info(user_add)
        app_add = add_groups_application(existing_group)
        logger.info(app_add)
        policy = assing_policy()
        logger.info(policy)
    else:
        logger.error("wrong input please try again!!!!")
if __name__ == "__main__":
    main()