"""run-enaclient.py - run the ENAClient

This module can be used to run the ENAClient via the command line
"""

import sys
from enaclient.enaclient import ENAClient

def main():
    """run the ENAClient"""
    client = ENAClient()
    client.call_and_output_all()

if __name__ == "__main__":
    main()
