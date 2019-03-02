import os
import re
import argparse
import requests
import json
import yaml
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString

class ENAClient:

    API_BASE_URL = "https://www.ebi.ac.uk/ena/cram/"

    INPUT_MODE_SINGLE = 0
    INPUT_MODE_BATCH = 1

    OUTPUT_FORMAT_JSON = 0
    OUTPUT_FORMAT_XML = 1
    OUTPUT_FORMAT_YAML = 2

    OUTPUT_MODE_STDOUT = 0
    OUTPUT_MODE_FILE = 1

    def __init__(self):
        self.valid_args = False
        self.input_mode = ENAClient.INPUT_MODE_SINGLE
        self.output_format = ENAClient.OUTPUT_FORMAT_JSON
        self.output_mode = ENAClient.OUTPUT_MODE_STDOUT

        self.output_file = None
        self.args_dict = self.__parse_args()
        # print(ENAClient.API_BASE_URL)

    def __parse_args(self):

        parser = argparse.ArgumentParser("python enaclient.py")
        group_input_mode = parser.add_mutually_exclusive_group()
        sequence_id_arg = group_input_mode.add_argument('-s', '--sequence_id', type=str, help="sequence id (not compatible with -i option)")
        group_input_mode.add_argument('-i', '--input_file', type=str, help="input file containing sequence ids (not compatible with -s option)")

        output_format_arg = parser.add_argument('-f', '--output_format', type=str, help="output format, specify [text|json|xml]. (optional, will output text by default)")
        parser.add_argument('-o', '--output_file', type=str, help="path to output file (optional, will print to stdout by default)")

        args_dict = None

        try:
            args_dict = vars(parser.parse_args())

            if not args_dict["sequence_id"] and not args_dict["input_file"]:
                raise ValueError("ERROR: sequence id/input file not specified. Specify sequence id with -s or input file with -i\n")

            if args_dict["input_file"]:
                self.input_mode = ENAClient.INPUT_MODE_BATCH
                if not os.path.exists(args_dict["input_file"]):
                    raise FileNotFoundError("ERROR: input file not found: %s\n" % (args_dict["input_file"]))


            if args_dict["output_format"] == "json" or args_dict["output_format"] == None:
                pass
            elif args_dict["output_format"] == "xml":
                self.output_format = ENAClient.OUTPUT_FORMAT_XML
            elif args_dict["output_format"] == "yaml":
                self.output_format = ENAClient.OUTPUT_FORMAT_YAML
            else:
                raise argparse.ArgumentError(output_format_arg, "invalid output format, specify json, xml, or yaml\n")

            if args_dict["output_file"]:
                self.output_mode = ENAClient.OUTPUT_MODE_FILE
                dirname = os.path.dirname(args_dict["output_file"])
                if not os.path.exists(dirname) and dirname != "":
                    raise FileNotFoundError("ERROR: output directory does not exist: %s\n" % (dirname))


            self.valid_args = True

        except argparse.ArgumentError as e:
            print(e)
            parser.print_help()
        except ValueError as e:
            print(e)
            parser.print_help()
        except FileNotFoundError as e:
            print(e)
            parser.print_help()


        return args_dict

    def query_ena_all(self):

        if self.valid_args:

            if self.output_mode == ENAClient.OUTPUT_MODE_FILE:
                self.output_file = open(self.args_dict["output_file"], "a")

            self.__output_batch_prefix()

            if self.input_mode == ENAClient.INPUT_MODE_BATCH:
                input_file = open(self.args_dict["input_file"], "r")
                input_line = input_file.readline()
                while (input_line):
                    sequence_id = input_line.rstrip()
                    response_string = self.query_ena(sequence_id)

                    input_line = input_file.readline()
                    if input_line:
                        self.__output(response_string)
                        self.__output_batch_separator()
                    else:
                        self.__output(response_string + "\n")

            else:
                sequence_id = self.args_dict["sequence_id"]
                response_string = self.query_ena(sequence_id)
                self.__output(response_string + "\n")

            self.__output_batch_suffix()

    def query_ena(self, sequence_id):
        endpoint = ENAClient.API_BASE_URL + "sequence/" + sequence_id + "/metadata"
        response_dict = {"req_seq_id": sequence_id}
        response_string = ""

        try:
            response_obj = requests.get(endpoint, timeout=10)
            response_dict["status_code"] = response_obj.status_code
            response_dict.update(response_obj.json())

        except requests.exceptions.ConnectTimeout as e:
            response_dict["status_code"] = "408"
            response_dict["error"] = "connection timeout"
        finally:
            # json
            if self.output_format == ENAClient.OUTPUT_FORMAT_JSON:
                response_string = json.dumps(response_dict, indent=4)
            # xml
            elif self.output_format == ENAClient.OUTPUT_FORMAT_XML:
                xml = dicttoxml(response_dict, custom_root="sequence", attr_type=False)
                dom = parseString(xml)
                response_string = dom.toprettyxml()[:-1]
                response_string = re.sub("<\?xml.+?>\n", "", response_string)
            # yaml
            elif self.output_format == ENAClient.OUTPUT_FORMAT_YAML:
                response_string = yaml.dump(response_dict)[:-1]

            response_string = re.sub("(.+?\n)", r'\t\1', response_string)
            response_string = re.sub("\n(.+?$)", r'\n\t\1', response_string)

        return response_string

    def __output_batch_prefix(self):
        prefixes_dict = {
            ENAClient.OUTPUT_FORMAT_JSON: "[\n",
            ENAClient.OUTPUT_FORMAT_XML: '<?xml version="1.0" ?>\n<sequence_group>\n',
            ENAClient.OUTPUT_FORMAT_YAML: "sequence_group:\n"
        }
        self.__output(prefixes_dict[self.output_format])

    def __output_batch_separator(self):
        separators_dict = {
            ENAClient.OUTPUT_FORMAT_JSON: ",\n",
            ENAClient.OUTPUT_FORMAT_XML: "\n",
            ENAClient.OUTPUT_FORMAT_YAML: "\n"
        }
        self.__output(separators_dict[self.output_format])

    def __output_batch_suffix(self):
        suffixes_dict = {
            ENAClient.OUTPUT_FORMAT_JSON: "]",
            ENAClient.OUTPUT_FORMAT_XML: "</sequence_group>",
            ENAClient.OUTPUT_FORMAT_YAML: ""
        }
        self.__output(suffixes_dict[self.output_format])

    def __output(self, to_write):

        if self.output_mode == ENAClient.OUTPUT_MODE_STDOUT:
            print(to_write, end="")
        elif self.output_mode == ENAClient.OUTPUT_MODE_FILE:
            self.output_file.write(to_write)
