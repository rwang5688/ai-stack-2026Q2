# This function is used to register student to a course.
# The student id,course name and semester are passed as parameters. 
# The function stored student details in the Amazon DynamoDB.

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

    print("*** courseName:", courseName)
    
    # Find the "studentID" parameter from the list of parameters
    student_param = next((param for param in parameters if param['name'] == 'studentID'), None)
    if student_param:
        studentID = student_param['value']
    else:
        studentID = None  # Use a default value or handle the case where the parameter is not found

    print("*** courseName:", studentID)

    # Find the "semester" parameter from the list of parameters
    semester_param = next((param for param in parameters if param['name'] == 'semester'), None)
    if semester_param:
        semester = semester_param['value']
    else:
        semester = None  # Use a default value or handle the case where the parameter is not found

    print("*** courseName:", semester)

    try:
        reg_id = str(uuid.uuid4())

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('course_registration')
        response = table.put_item(
            Item={
                'reg_id': reg_id,
                'student_id': studentID,
                'course_name': courseName, 
                'semester': semester
            }
        )
        db_response = "registrationStatus: Registered successfully. A notification was sent to your student email with  for registrationd details for " + courseName
    
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
        
        print("*** end of function****")

        dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
        
        print("Response: {}".format(dummy_function_response))

    return dummy_function_response
