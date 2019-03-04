[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.4+](https://img.shields.io/badge/python-3.4+-blue.svg)](https://www.python.org/downloads/release/python-372/)
![Travis (.org)](https://img.shields.io/travis/jb-adams/enaclient.svg)
[![Coverage Status](https://coveralls.io/repos/github/jb-adams/enaclient/badge.svg?branch=master)](https://coveralls.io/github/jb-adams/enaclient?branch=master)

# enaclient
command-line client for retrieving ENA sequence metadata through GA4GH refget API

The enaclient can be used to retrieve ENA sequence metadata through the refget API. Requests can be submitted in single or batch mode, and returned metadata can be formated as JSON, XML, or YAML. Responses can be printed to screen or written to an output file.

Note: Due to dependencies, enaclient is compatible with Python versions 3.4 or higher.

## Installation

Provided that python3 is already installed on the local machine, execute the following steps to set up the enaclient:

1. Clone enaclient repository to local machine:
```bash
git clone https://github.com/jb-adams/enaclient.git
```
2. Enter enaclient directory and install dependencies:
```bash
cd enaclient
pip install -r requirements.txt
```
3. Install the enaclient library
```bash
python setup.py install
```
3. Enter the scripts directory and execute the run-enaclient.py script via python
```bash
cd scripts
python run-enaclient.py
```

## Usage

### Basic usage

The enaclient can be executed through python3 from the command-line:
```bash
python run-enaclient.py
```

Use the -h parameter to display the help dialog:
```bash
python run-enaclient.py -h
```

Specify a sequence id/md5sum with the "-s" parameter to get associated metadata
```bash
# template
python run-enaclient.py -s ${SEQUENCE_ID}
# example
python run-enaclient.py -s 3050107579885e1608e6fe50fae3f8d0
```

### Run in batch mode
By default, the enaclient only gets metadata for a single sequence id. The enaclient can also be run in batch mode, where metadata is retrieved for multiple sequence ids. To run in batch mode, write a text file with each sequence id of interest on a separate line. <br/><br/>Example input file:
```bash
3050107579885e1608e6fe50fae3f8d0
3050107579885e1608e6fe50fae3f8d1
3050107579885e1608e6fe50fae3f8d2
3050107579885e1608e6fe50fae3f8d3
3050107579885e1608e6fe50fae3f8d4
```

To run enaclient in batch mode, specify the input file with the -i/--input_file parameter. In the example below, the input file is located at data/sequence_ids.txt. Note: the -s and -i options are mutually exclusive.
```bash
# template
python run-enaclient.py -i ${INPUT_FILE}
# example
python run-enaclient.py -i data/sequence_ids.txt
```

### Specify output format
By default, sequence metadata is returned in JSON format. The enaclient can also display metadata in XML and YAML. Specify output format with the -f/--output_format parameter.
```bash
# template
python run-enaclient.py -i ${INPUT_FILE} -f ${FORMAT}
# example - display metadata in XML
python run-enaclient.py -i ${INPUT_FILE} -f xml
# example - display metadata in YAML
python run-enaclient.py -i ${INPUT_FILE} -f yaml
```

### Write to an output file
By default, sequence metadata is printed to stdout. The enaclient can also write metadata to an output file. Specify the output file with the -o/--output_file parameter.
```bash
# template
python run-enaclient.py -i ${INPUT_FILE} -o ${OUTPUT_FILE}
# example
python run-enaclient.py -i data/sequence_ids.txt -o data/metadata.json
```
