"""testall.py - test ENAClient scenarios

This module contains test scenarios for the ENAClient.
"""

import sys
from enaclient.enaclient import ENAClient

# define arguments that will be passed to the ENAClient through the arg parser
sequence_id_0 = "3050107579885e1608e6fe50fae3f8d0"
input_file_0 = "testdata/input.txt"
output_file_0 = "testdata/output.json"
output_file_1 = "testdata/output.xml"
output_file_2 = "testdata/output.yaml"

# argument sets that are designed to raise an exception
args_error_0 = []
args_error_1 = ["-i", "nofile.txt"]
args_error_2 = ["-s", sequence_id_0, "-f", "wrongformat"]
args_error_3 = ["-s", sequence_id_0, "-o", "wrongdir/wrongfile.txt"]

# argument sets that are designed to run the ENAClient to completion
args_success_0 = ["-s", sequence_id_0]
args_success_1 = ["-s", sequence_id_0, "-f" "xml"]
args_success_2 = ["-s", sequence_id_0, "-f" "yaml"]
args_success_3 = ["-s", sequence_id_0, "-o", output_file_0]
args_success_4 = ["-i", input_file_0, "-o", output_file_0]
args_success_5 = ["-s", sequence_id_0, "-o", output_file_1, "-f", "xml"]
args_success_6 = ["-s", sequence_id_0, "-o", output_file_2, "-f", "yaml"]

def test_parse_args():
    """test the ENAClient __parse_args method"""

    # assert ValueError raised - seq id and input file not specified
    client = ENAClient(args=args_error_0)
    assert client.get_parser_error().__class__.__name__ == "ValueError"

    # assert FileNotFoundError raised
    client = ENAClient(args=args_error_1)
    assert client.get_parser_error().__class__.__name__ == "FileNotFoundError"

    # assert ArgumentError raised
    client = ENAClient(args=args_error_2)
    assert client.get_parser_error().__class__.__name__ == "ArgumentError"

    # assert FileNotFoundError raised - no output directory
    client = ENAClient(args=args_error_3)
    assert client.get_parser_error().__class__.__name__ == "FileNotFoundError"

    # assert sequence id correctly assigned
    client = ENAClient(args=args_success_1)
    assert client.get_args_dict()["sequence_id"] == sequence_id_0

    # assert format is xml
    client = ENAClient(args=args_success_1)
    assert client.get_output_format() == ENAClient.OUTPUT_FORMAT_XML

    # assert format is yaml
    client = ENAClient(args=args_success_2)
    assert client.get_output_format() == ENAClient.OUTPUT_FORMAT_YAML

def test_call_and_output_all():
    """test the ENAClient call_and_output_all method"""

    # assert ConnectTimeout raised
    client = ENAClient(args=args_success_0)
    client.set_timeout_secs(0.0001)
    client.call_and_output_all()
    assert client.get_connect_error().__class__.__name__ == "ConnectTimeout"

    # assert call and output all method runs in single, json mode
    client = ENAClient(args=args_success_0)
    client.call_and_output_all()

    # assert output file is written to and check output matches template
    client = ENAClient(args=args_success_3)
    client.call_and_output_all()
    output = open(output_file_0, "r").read().rstrip()
    assert output == open("testdata/response_2.json", "r").read().rstrip()

    # assert input file is read and client executed in batch mode
    # assert output matches template
    client = ENAClient(args=args_success_4)
    client.call_and_output_all()
    output = open(output_file_0, "r").read().rstrip()
    assert output == open("testdata/response_3.json", "r").read().rstrip()

    # assert query all executed for xml format
    # assert output matches template
    client = ENAClient(args=args_success_5)
    client.call_and_output_all()
    output = open(output_file_1, "r").read().rstrip()
    assert output == open("testdata/response_1.xml", "r").read().rstrip()

    # assert query all executed for yaml format
    client = ENAClient(args=args_success_6)
    client.call_and_output_all()
    output = open(output_file_2, "r").read().rstrip()
    assert output == open("testdata/response_1.yaml", "r").read().rstrip()

def test_call_refget_api():
    """test the ENAClient call_refget_api method"""

    # assert that json output matches expected response
    client = ENAClient(args=args_success_0)
    response_string = client.call_refget_api(sequence_id_0, 0)
    correct_output = open("testdata/response_1.json", "r").read().rstrip()
    assert response_string == correct_output
