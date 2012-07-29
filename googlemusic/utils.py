"""
Utility functions
"""
__author__ = "Tirino"

MAC_ADDRESS_SEPARATOR = ':'

import os
import re
import subprocess
import uuid

def get_from_text(what, where):
    """Find regular expression [what] in [where] and return it"""
    return re.search(what, where, re.MULTILINE).group(1)

def run_command(cmd):
    """Run a native command"""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, shell=True)
    out, errors = proc.communicate()
    if not errors:
        return str(out).strip()
    else:
        raise Exception(str(errors))

def get_computer_name():
    """Return the 'Computer Name' or the hostname"""
    name = None
    if os.uname()[0] == 'Darwin':
        try:
            name = run_command('scutil --get ComputerName')
        except:
            pass
    # if we don't have a name already, try uname()
    if not name:
        output = os.uname()[1]
        if output:
            name = output
        else:
            try: # for Windows only
                name = os.getenv('COMPUTERNAME')
            except:
                pass
    return name

def get_mac_address():
    """Return the computer main MAC address"""
    mac = '%012x' % uuid.getnode()
    mac_parts = [mac[x:x+2] for x in range(0, len(mac), 2)]
    return MAC_ADDRESS_SEPARATOR.join(mac_parts).upper()

