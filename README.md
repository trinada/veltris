This is code is to create a user in JumCloud and itegrate it to a SSO application in AWS. 
There is manual intervention needed in place where user has to configure user and SSo application details. 

## Creation of User

The user creation uses endpoint that allows you to create a bulk job. The absolute requirements are described in Attributes which are taken as headder for POST call to end point. We are gathering the jobID from the earlier operation and track it see the process for creation of an userid which is uniqure to every user. 

## Creation of User Groups
The Group creation is a static allocation to group users. We need an unique group name for the post call and we track usergroupId for uder in future. 
We also run against existing usergroups which can be used to allocate users to perdefiend comfoiguration under these groups. For every userGroup we need a groupId in order to integrate a user and Group 

## Adding user to UserGroups

 Given as a choice to add the user to an existing group or to new group. UserID and groupID is required in order to integrate each of them. 
 
 url = "https://console.jumpcloud.com/api/v2/usergroups/{0}/members".format(existing_group_id)

    payload = {
        "id": user_id,
        "op": "add",
        "type": "user"
    }
## Adding Group  to Application 
We have gathered the existing application which are manually created and itegrated to AWS. We list applicationId and see which groups  are already integrated and if not then we add the group. 
    
    url = "https://console.jumpcloud.com/api/v2/applications/{0}/associations".format(app_id)
    payload = {
        "id": group_id,
        "op": "add",
        "attributes": {},
        "type": "user_group"
    }


### AWS Assgining policies to the roles Associated 

We are using boto3 session as base to interact with AWS. 
We are attaching policy to the role desribed in the following and recording the response. 

    response = client.attach_role_policy(PolicyArn='arn:aws:iam::478004422427:policy/test_policy', RoleName='sso_admin')
post this we are verfying weather there is policy attached to role and recordong and logging it. 

        policies = client.list_attached_role_policies(**params)
        for p in policies["AttachedPolicies"]:
            logger.info(f"the policy attached are {p}")
## wAWS Testing with EC2

Assuption is the user should be able to created,dwscribe instaces but delete operation is not application as the policy is defined. 

    ec2_console.run_instances(ImageId = 'ami-01816d07b1128cd2d',MaxCount=1,MinCount=1,InstanceType='t2.micro')

we fetchiing the instanceID created and testing the deletion opration besed on it. 

        instance_id = ec2_console.describe_instances()['Reservations'][2]['Instances'][0]['InstanceId']
        ec2_console.terminate_instances(InstanceIds= [instance_id])
        

