import json
import os

def handler(event, context):
    """
    Netlify serverless function to serve water quality data
    Returns the contents of water_quality_data.json
    """
    try:
        # Get the path to the JSON file
        # In Netlify, the file will be in the root directory
        json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'water_quality_data.json')
        
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Return successful response with CORS headers
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps(data, ensure_ascii=False)
        }
        
    except FileNotFoundError:
        # Handle case where JSON file is not found
        error_response = {
            'error': 'Water quality data file not found',
            'message': 'The water_quality_data.json file could not be located'
        }
        
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps(error_response)
        }
        
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        error_response = {
            'error': 'Invalid JSON data',
            'message': f'Failed to parse water quality data: {str(e)}'
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps(error_response)
        }
        
    except Exception as e:
        # Handle any other unexpected errors
        error_response = {
            'error': 'Internal server error',
            'message': f'An unexpected error occurred: {str(e)}'
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps(error_response)
        }
