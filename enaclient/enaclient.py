"""enaclient.py - retrieve ENA sequence metadata through refget API

This module contains the class ENAClient. The ENAClient can retrieve sequence
metadata through the refget API. Requests can be submitted in single or batch
mode, and returned metadata can be formated as JSON, XML, or YAML.
"""

import os
import sys
import re
import argparse
import requests
import json
import yaml
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString

class ENAClient:
    """Retrieve ENA sequence metadata through refget API and format responses

    Parameters (input sequence id/file, output format, output mode, output file)
    are specified via the command line. The ENAClient calls the refget API,
    formats responses to the requested format, and outputs metadata to stdout
    or output file.
    """

    # class/static variables
    API_BASE_URL = "https://www.ebi.ac.uk/ena/cram/"

    INPUT_MODE_SINGLE = 0
    INPUT_MODE_BATCH = 1

    OUTPUT_FORMAT_JSON = 0
    OUTPUT_FORMAT_XML = 1
    OUTPUT_FORMAT_YAML = 2

    OUTPUT_MODE_STDOUT = 0
    OUTPUT_MODE_FILE = 1

    DEFAULT_TIMEOUT_SECS = 10

    def __init__(self, args=sys.argv[1:]):
        """instantiate the ENAClient

        Args:
            args (list): parameter specifications taken from command-line

        Returns:
            (class ENAClient): the ENAClient
        """

        # set default settings in case these properties are not overriden
        # via command-line args
        self.__set_input_mode(ENAClient.INPUT_MODE_SINGLE)
        self.__set_output_mode(ENAClient.OUTPUT_MODE_STDOUT)
        self.__set_output_format(ENAClient.OUTPUT_FORMAT_JSON)
        self.__set_output_file(None)
        self.__set_valid_args(False)
        self.set_timeout_secs(ENAClient.DEFAULT_TIMEOUT_SECS)

        # parse command-line args, changing properties as necessary
        # verify that a valid set of args was passed (ie passes error checks)
        self.__parse_args(args)

    def __parse_args(self, args):
        """parse command-line args, changing properties as necessary

        Changes default internal attributes (input mode, output mode, etc.) if
        they are specified on command line. Also checks that a valid set of
        args was passed, ensuring the refget API call(s) will not occur if
        there is inconsistency in the command-line args.

        Args:
            args (list): parameter specifications taken from command-line

        Raises:
            ArgumentError: if invalid output format specified
            ValueError: if neither sequence id nor input file were provided
            FileNotFoundError: if input file or output directory not found
        """

        # add arguments to the parser, makes provisions for sequence id,
        # input file, output format, and output file
        # sequence id and input file are mutually exclusive
        parser = argparse.ArgumentParser("python enaclient.py")
        group_input_mode = parser.add_mutually_exclusive_group()
        sequence_id_arg = group_input_mode.add_argument('-s', '--sequence_id',
            type=str, help="sequence id (not compatible with -i option)")
        group_input_mode.add_argument('-i', '--input_file', type=str,
            help="input file containing sequence ids (not compatible with "
            + "-s option)")
        output_format_arg = parser.add_argument('-f', '--output_format',
            type=str, help="output format, specify [text|json|xml]. (optional, "
            + "will output text by default)")
        parser.add_argument('-o', '--output_file', type=str,
            help="path to output file (optional, will print to stdout by "
            + "default)")

        args_dict = None

        try:
            args_dict = vars(parser.parse_args(args)) # set parsed args to dict

            # check for either sequence id or input file, raise ValueError
            # if neither specified
            if not args_dict["sequence_id"] and not args_dict["input_file"]:
                raise ValueError("ERROR: sequence id/input file not specified. "
                     + "Specify sequence id with -s or input file with -i\n")

            # set input mode to "batch" instead of "single" if input file
            # specified. check input file exists, raise FileNotFoundError
            # otherwise
            if args_dict["input_file"]:
                self.__set_input_mode(ENAClient.INPUT_MODE_BATCH)
                if not os.path.exists(args_dict["input_file"]):
                    raise FileNotFoundError("ERROR: input file not found: "
                        + "%s\n" % (args_dict["input_file"]))

            # set output format. default is json, can be changed to xml or
            # yaml if correct arg provided. if format arg is anything else
            # other than json, xml, or yaml, raise ArgumentError
            if args_dict["output_format"] in set(["json", None]):
                pass
            elif args_dict["output_format"] == "xml":
                self.__set_output_format(ENAClient.OUTPUT_FORMAT_XML)
            elif args_dict["output_format"] == "yaml":
                self.__set_output_format(ENAClient.OUTPUT_FORMAT_YAML)
            else:
                raise argparse.ArgumentError(output_format_arg,
                    "invalid output format, specify json, xml, or yaml\n")

            # set output mode to file instead of stdout if output file provided
            # check that output directory exists, raise FileNotFoundError if not
            if args_dict["output_file"]:
                self.__set_output_mode(ENAClient.OUTPUT_MODE_FILE)
                dirname = os.path.dirname(args_dict["output_file"])
                if not os.path.exists(dirname) and dirname != "":
                    raise FileNotFoundError("ERROR: output directory does not "
                        + "exist: %s\n" % (dirname))

            # if no errors are raised, set "_valid_args" to true, meaning that
            # the rest of the program can proceed
            self.__set_valid_args(True)

        # if error encountered, set the parser error attribute, and print the
        # arg parser help message
        except argparse.ArgumentError as e:
            self.__set_parser_error(e)
            print(e)
            parser.print_help()
        except ValueError as e:
            self.__set_parser_error(e)
            print(e)
            parser.print_help()
        except FileNotFoundError as e:
            self.__set_parser_error(e)
            print(e)
            parser.print_help()
        finally:
            # set the instance arguments dictionary to the parsed args
            self.__set_args_dict(args_dict)

    def call_and_output_all(self):
        """Output formatted responses from refget API requests

        This method only executes provided a valid set of command-line args
        was passed. Executes the metadata request for each sequence id, and
        writes/prints the formatted response.
        """

        args_dict = self.get_args_dict()
        inc = 0

        # only makes API call if there is a valid set of args
        if self.get_valid_args():

            # open the output file handle if applicable
            # first overwrite all the contents of the file, then close and
            # open the file again in append mode
            if self.get_output_mode() == ENAClient.OUTPUT_MODE_FILE:
                output_file_path = args_dict["output_file"]
                output_file_write = open(output_file_path, "w")
                output_file_write.write("")
                output_file_write.close()
                self.__set_output_file(open(output_file_path, "a"))

            # write/print prefix for array of metadata objects
            self.__output_batch_prefix()

            # if input file was provided, then the program will iterate over
            # each sequence id in the file, making the API request for each
            # id. Formatted responses are printed/written as they are processed.
            if self.get_input_mode() == ENAClient.INPUT_MODE_BATCH:
                input_file = open(args_dict["input_file"], "r")
                input_line = input_file.readline()
                # while next input file line is not empty
                while (input_line):
                    # get the sequence id and get the formatted response
                    sequence_id = input_line.rstrip()
                    response_string = self.call_refget_api(sequence_id, inc)

                    input_line = input_file.readline()
                    # if there is another sequence id on the next line,
                    # output the formatted response and the separator char
                    # between returned objects
                    if input_line:
                        self.__output(response_string)
                        self.__output_batch_separator()
                    # if there are no more sequence ids (at end of file), then
                    # do not output the separator char
                    else:
                        self.__output(response_string + "\n")
                    inc += 1

            # sequence id was provided, program executed in single mode
            else:
                # get sequence id and send it to api call method, writing/
                # printing output
                sequence_id = args_dict["sequence_id"]
                response_string = self.call_refget_api(sequence_id, inc)
                self.__output(response_string + "\n")

            # write/print suffix for array of metadata objects
            self.__output_batch_suffix()

            if self.get_output_mode() == ENAClient.OUTPUT_MODE_FILE:
                self.get_output_file().close()

    def call_refget_api(self, sequence_id, inc):
        """Execute refget API request and return formatted response

        This method calls the refget API to get ENA sequence metadata for a
        provided sequence id. The response is formatted according to the
        user-specified output format.

        Args:
            sequence_id (str): md5sum/id for the sequence of interest
            inc (int): auto-increment input sequence

        Returns:
            response_string (str): json/xml/yaml formatted API response

        Raises:
            requests.exceptions.ConnectTimeout: if API does not respond within
                the specified time limit
        """

        # construct the endpoint for the API request
        endpoint = ENAClient.API_BASE_URL + "sequence/" + sequence_id \
                   + "/metadata"

        # initialize the response object with the user-specified sequence id
        response_dict = {"req_seq_id": sequence_id}
        response_string = ""

        try:

            # make http request, adding http response code to what will be
            # output (200 if sequence metadata found and returned, 404 if
            # the sequence id could not be found.
            response_obj = requests.get(endpoint,
                                        timeout=self.get_timeout_secs())
            response_dict["status_code"] = response_obj.status_code
            # update the response dictionary with the returned metadata
            response_dict.update(response_obj.json())

        # if connection timed out, set status code to "408" so user knows
        # there was a timeout
        except requests.exceptions.ConnectTimeout as e:
            self.__set_connect_error(e)
            response_dict["status_code"] = "408"
            response_dict["error"] = "connection timeout"

        # format the response dictionary according to output format
        finally:
            # format response as json
            output_format = self.get_output_format()
            if output_format == ENAClient.OUTPUT_FORMAT_JSON:
                response_string = json.dumps(response_dict, indent=4)
            # format response as xml
            elif output_format == ENAClient.OUTPUT_FORMAT_XML:
                xml = dicttoxml(response_dict, custom_root="sequence",
                                attr_type=False)
                dom = parseString(xml)
                response_string = dom.toprettyxml(indent="    ")[:-1]
                response_string = re.sub("<\\?xml.+?>\n", "", response_string)
            # format response as yaml
            elif output_format == ENAClient.OUTPUT_FORMAT_YAML:
                response_string = yaml.dump(response_dict)[:-1]
                response_string = re.sub("(.+?\n)", r'    \1', response_string)
                response_string =  re.sub("\n(.+?$)", r'\n    \1',
                                   response_string)
                response_string = "sequence_%s:\n" % (inc) + response_string

            # indent all lines in response string, to account for the fact that
            # each object is one element in an overall array
            response_string = re.sub("(.+?\n)", r'    \1', response_string)
            response_string = re.sub("\n(.+?$)", r'\n    \1', response_string)

        return response_string

    def __output_batch_prefix(self):
        """Write/print prefix for array of metadata objects based on format"""

        # write prefix that opens the array of metadata objects
        prefixes_dict = {
            ENAClient.OUTPUT_FORMAT_JSON: "[\n",
            ENAClient.OUTPUT_FORMAT_XML: '<?xml version="1.0" ?>\n'
                                         + '<sequence_group>\n',
            ENAClient.OUTPUT_FORMAT_YAML: "sequence_group:\n"
        }
        self.__output(prefixes_dict[self.get_output_format()])

    def __output_batch_separator(self):
        """Write/print char(s) that separate elements in array of objs"""

        # write character(s) the separate metadata responses, as each response
        # is an element in an overall array
        separators_dict = {
            ENAClient.OUTPUT_FORMAT_JSON: ",\n",
            ENAClient.OUTPUT_FORMAT_XML: "\n",
            ENAClient.OUTPUT_FORMAT_YAML: "\n\n"
        }
        self.__output(separators_dict[self.get_output_format()])

    def __output_batch_suffix(self):
        """Write/print suffix for array of metadata objects based on format"""

        # write suffix that closes the array of metadata objects

        suffixes_dict = {
            ENAClient.OUTPUT_FORMAT_JSON: "]",
            ENAClient.OUTPUT_FORMAT_XML: "</sequence_group>",
            ENAClient.OUTPUT_FORMAT_YAML: ""
        }
        self.__output(suffixes_dict[self.get_output_format()])

    def __output(self, to_write):
        """Write/print output based on user specification

        Args:
            to_write (str): string to be printed/written to file
        """

        # if output mode is set to stdout, print the provided string,
        # otherwise write it to the output file
        output_mode = self.get_output_mode()

        if output_mode == ENAClient.OUTPUT_MODE_STDOUT:
            print(to_write, end="")
        elif output_mode == ENAClient.OUTPUT_MODE_FILE:
            output_file = self.get_output_file()
            output_file.write(to_write)

    "Setter Methods"

    def __set_input_mode(self, input_mode):
        """set input mode

        Args:
            input_mode (int): input mode
        """
        self._input_mode = input_mode

    def __set_output_format(self, output_format):
        """set output format

        Args:
            output_format (int): output format
        """
        self._output_format = output_format

    def __set_output_mode(self, output_mode):
        """set output mode

        Args:
            output_mode (int): output mode
        """
        self._output_mode = output_mode

    def __set_output_file(self, output_file):
        """set output file

        Args:
            output_file (file): output file handle
        """
        self._output_file = output_file

    def __set_valid_args(self, valid_args):
        """set valid args

        Args:
            valid_args (bool): valid args (true if cli args are valid)
        """
        self._valid_args = valid_args

    def __set_args_dict(self, args_dict):
        """set args dict

        Args:
            args_dict (dict): command line arguments dictionary
        """
        self.args_dict = args_dict

    def __set_parser_error(self, parser_error):
        """set parser error

        Args:
            parser_error (obj): error object
        """
        self.parser_error = parser_error

    def __set_connect_error(self, connect_error):
        """set connect error

        Args:
            connect_error (obj): error object
        """
        self.connect_error = connect_error

    def set_timeout_secs(self, timeout_secs):
        """set timeout secs

        Args:
            timeout_secs (float): timeout secs
        """
        self.timeout_secs = timeout_secs

    "Getter Methods"

    def get_input_mode(self):
        """get input mode

        Returns:
            _input_mode (int): input mode
        """
        return self._input_mode

    def get_output_format(self):
        """get output format

        Returns:
            _output_format (int): output format
        """
        return self._output_format

    def get_output_mode(self):
        """get output mode

        Returns:
            _output_mode (int): output mode
        """
        return self._output_mode

    def get_output_file(self):
        """get output file

        Returns:
            _output_file (file): output file handle
        """
        return self._output_file

    def get_valid_args(self):
        """get valid args

        Returns:
            _valid_args (bool): true if correct set of cli args provided
        """
        return self._valid_args

    def get_args_dict(self):
        """get args dictionary

        Returns:
            args_dict (dict): dictionary of cli args
        """
        return self.args_dict

    def get_parser_error(self):
        """get parser error

        Returns:
            parser_error (obj): error object
        """
        return self.parser_error

    def get_connect_error(self):
        """get connect error

        Returns:
            connect_error (obj): error object
        """
        return self.connect_error

    def get_timeout_secs(self):
        """get timeout secs

        Returns:
            timeout_secs (float): timeout secs
        """
        return self.timeout_secs
