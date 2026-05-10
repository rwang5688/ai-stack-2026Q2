# This function is used to get the course reviews for a particular course.
# The course name is passed as a parameter.
# The function fetches course review froms the Amazon DynamoDB and returns the course reviews for the course.

import json
import boto3
import uuid


from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    response_code = 200
    
    # Find the "course" parameter from the list of parameters
    course_param = next((param for param in parameters if param['name'] == 'course'), None)
    if course_param:
        courseName = course_param['value']
    else:
        courseName = None  # Use a default value or handle the case where the parameter is not found

    print ("*** courseName:", courseName)

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('course_reviews')
           
        #response = table.query( KeyConditionExpression=Key('course_name').eq(courseName))
        # Hack: Take a substring of the first 6 characters of courseName, e.g., CS 441 Machine Learning -> CS 441.
        response = table.query( KeyConditionExpression=Key('course_name').eq(courseName[0:6]))
    
        if response['Items']:
           db_response =  json.dumps(response)
        else:
           db_response = "No records found"
    except Exception as e: 
           print("DB Error:", e)
           db_response = "DB Error"
    finally:
            # Execute your business logic here. For more information, refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
            responseBody =  {
                "TEXT": {
                    "body": "Reviews {}".format(db_response)
                }
            }
        
            action_response = {
                'actionGroup': actionGroup,
                'httpStatusCode': response_code,
                'function': function,
                'functionResponse': {
                     'responseBody': responseBody
                }
            }
            
            print ("*** end of function****")

            dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
            
            print("Response: {}".format(dummy_function_response))

    return dummy_function_response
