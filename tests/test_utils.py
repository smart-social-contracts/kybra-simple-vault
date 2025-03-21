import subprocess
import ast
import json
import traceback
import requests
import ggg.utils as utils
import os
import logging
from typing import Union, List, Dict, Any
from datetime import datetime
import inspect

# Constants
DFX_COMMAND = 'dfx'
TEST_LOCAL_ENV = 'TEST_LOCAL'
RUN_CODE_ENDPOINT = 'run_code'
DEBUG_FILE_DIR = '/app/debug_files'

def make_http_request(endpoint, method='GET', data=None):
    """Make HTTP request to local server"""
    base_url = 'http://localhost:8000'
    url = f"{base_url}/{endpoint}"

    print(f"Making HTTP request: {method} {url}")
    
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        response = requests.post(url, data=data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
        
    return response.text


def _parse_dfx_command(command: List[str]) -> tuple[str, str, Union[str, None]]:
    """Parse dfx command into HTTP request parameters.
    
    Args:
        command: List of command components
        
    Returns:
        Tuple of (endpoint, method, data)
    """
    endpoint = '/'.join(command[4:])  # After ['dfx', 'canister', 'call', 'canister_main']
    method = 'GET'
    data = None
    
    if endpoint.startswith(RUN_CODE_ENDPOINT):
        method = 'POST'
        data = endpoint[len(RUN_CODE_ENDPOINT + '/'):]
        endpoint = RUN_CODE_ENDPOINT
        
    return endpoint, method, data

def _get_debug_filename(base_name: str, test_name: str) -> str:
    """Generate debug filename with timestamp and test info.
    
    Args:
        base_name: Base name of the file (gotten/expected)
        test_name: Name of the test scenario
        
    Returns:
        Formatted filename with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    debug_file_dir = './debug_files' if os.environ.get(TEST_LOCAL_ENV) else DEBUG_FILE_DIR
    # Create debug files directory if it doesn't exist
    os.makedirs(debug_file_dir, exist_ok=True)
    return os.path.join(debug_file_dir, f"{test_name}_{base_name}_{timestamp}.json")

def check(command: List[str], expected: Union[Dict, List, str], test_name: str = None) -> int:
    """Compare command output against expected result.
    
    Args:
        command: Command to execute as list of strings
        expected: Expected output (dict, list or string)
        test_name: Name of the test scenario. If None, will try to detect from call stack
        
    Returns:
        0 if output matches expected, 1 otherwise
    """
    # If test_name not provided, try to get it from the calling function
    if test_name is None:
        try:
            frame = inspect.currentframe()
            calling_frame = frame.f_back
            if calling_frame:
                test_name = calling_frame.f_code.co_name
        except Exception:
            test_name = "unknown_test"
        finally:
            del frame  # Avoid reference cycles

    if os.environ.get(TEST_LOCAL_ENV):
        if command[0] == DFX_COMMAND:
            endpoint, method, data = _parse_dfx_command(command)
        else:
            endpoint = command
            method = 'GET'
            data = None
            
        gotten = make_http_request(endpoint, method, data)
    else:
        # Original dfx command execution
        gotten = subprocess.run(command, capture_output=True, text=True).stdout

    is_dfx = command[0] == DFX_COMMAND
    
    if isinstance(expected, (dict, list)):
        if is_dfx and not os.environ.get(TEST_LOCAL_ENV):
            try:
                gotten = utils.parse_dfx_answer(gotten)
            except Exception as e:
                logging.error(f"Failed to parse DFX JSON response: {gotten}")
                logging.error(f"Error: {str(e)}")
                logging.error(f"Got type: {type(gotten)}, value: {gotten}")
                logging.error(f"Expected type: {type(expected)}, value: {expected}")
                raise
        else:
            try:
                gotten = json.loads(gotten)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode JSON: {gotten}")
                logging.error(f"Error: {str(e)}")
                raise
    else:
        gotten = str(gotten).strip()
        expected = str(expected).strip()

    if isinstance(gotten, (dict, list)) and isinstance(expected, (dict, list)):
        ret = 0 if utils.compare_json(expected, gotten) else 1
    else:
        ret = int(gotten != expected)

    if ret:
        logging.error(f"Comparison failed:")
        logging.error(f"Got type: {type(gotten)}, value: {json.dumps(gotten)}")
        logging.error(f"Expected type: {type(expected)}, value: {json.dumps(expected)}")
        
        try:
            # Save debug files
            gotten_file = _get_debug_filename("gotten", test_name)
            expected_file = _get_debug_filename("expected", test_name)
            
            with open(gotten_file, 'w') as f:
                f.write(json_dumps_for_test(gotten))
            with open(expected_file, 'w') as f:
                f.write(json_dumps_for_test(expected))
                
            logging.error(f"Debug files written to: {gotten_file} and {expected_file}")
        except Exception as e:
            logging.warning(f"Failed to save debug files: {str(e)}")
            
    return ret


def json_dumps_for_test(data):
    return json.dumps(data, sort_keys=True, indent=4)