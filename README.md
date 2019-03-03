[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Travis (.org)](https://img.shields.io/travis/jb-adams/enaclient.svg)
[![Python 3.4+](https://img.shields.io/badge/python-3.4+-blue.svg)](https://www.python.org/downloads/release/python-372/)

# enaclient
command-line client for retrieving ENA sequence metadata through GA4GH refget API

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
3. Execute enaclient script via python
```bash
python enaclient.py
```


## Usage

### Basic usage

The enaclient can be executed through python3 from the command-line:
```bash
python enaclient.py
```

Use the -h parameter to display the help dialog:
```bash
python enaclient.py -h
```

Specify a sequence id/md5sum with the "-s" parameter to get associated metadata
```bash
# template
python enaclient.py -s ${SEQUENCE_ID}
# example
python enaclient.py -s 3050107579885e1608e6fe50fae3f8d0
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

To run enaclient in batch mode, specify the input file with the -i/--input_file parameter. Note: the -s and -i options are mutually exclusive.
```bash
# template
python enaclient.py -i ${INPUT_FILE}
# example
python enaclient.py -i data/sequence_ids.txt
```

### Specify output format
By default, sequence metadata is returned in JSON format. The enaclient can also display metadata in XML and YAML. Specify output format with the -f/--output_format parameter.
```bash
# template
python enaclient.py -i ${INPUT_FILE} -f ${FORMAT}
# example - display metadata in XML
python enaclient.py -i ${INPUT_FILE} -f xml
# example - display metadata in YAML
python enaclient.py -i ${INPUT_FILE} -f yaml
```

### Write to an output file
By default, sequence metadata is printed to stdout. The enaclient can also write metadata to an output file. Specify the output file with the -o/--output_file parameter.
```bash
# template
python enaclient.py -i ${INPUT_FILE} -o ${OUTPUT_FILE}
# example
python enaclient.py -i data/sequence_ids.txt -o data/metadata.json
```
