import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import app

def handler(event, context):
    """Netlify function handler for Flask app"""
    from werkzeug.wrappers import Request, Response
    from werkzeug.serving import WSGIRequestHandler
    import io
    
    # Create a WSGI environ from the Netlify event
    environ = {
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),
        'SCRIPT_NAME': '',
        'PATH_INFO': event.get('path', '/'),
        'QUERY_STRING': event.get('queryStringParameters', ''),
        'CONTENT_TYPE': event.get('headers', {}).get('content-type', ''),
        'CONTENT_LENGTH': str(len(event.get('body', ''))),
        'SERVER_NAME': event.get('headers', {}).get('host', 'localhost'),
        'SERVER_PORT': '443',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': io.StringIO(event.get('body', '')),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add headers to environ
    for key, value in event.get('headers', {}).items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = 'HTTP_' + key
        environ[key] = value
    
    # Call the Flask app
    response_data = []
    def start_response(status, headers):
        response_data.append(status)
        response_data.append(headers)
    
    app_response = app(environ, start_response)
    
    # Format response for Netlify
    body = b''.join(app_response).decode('utf-8')
    status_code = int(response_data[0].split(' ')[0])
    headers = dict(response_data[1])
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body
    }
