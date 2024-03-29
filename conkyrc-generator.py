#!/usr/bin/env python3

import sys, os, subprocess, re
from jinja2 import Environment, FileSystemLoader, Template

def ram_info():
    meminfo_regex = re.compile(r'(.+):\s+(\S+) kB')

    with open('/proc/meminfo') as f:
        lines = f.readlines()
        for line in lines:
            m = meminfo_regex.match(line)
            if m:
                var   = m.group(1)
                value = m.group(2)
                if var == 'MemTotal':
                    ram_size = int(value)
                elif var == 'SwapTotal':
                    swap_size = int(value)

        config['ram_size'] = round(ram_size / 1024 / 1024, 2)

        if swap_size > 0:
            config['swap'] = True
        else:
            config['swap'] = False

def cpu_info():
    lscpu_regex = re.compile(r'(.+):\s+(.+)')
    cpu_number = cpu_model = None

    try:
        output = subprocess.check_output(["lscpu"]).decode('utf-8')
    except FileNotFoundError:
        print('lscpu not found :O', file=sys.stderr)
        return False
    except subprocess.CalledProcessError:
        print('lscpu blew up :(', file=sys.stderr)
        return False

    lines = output.split('\n')
    for line in lines:
        m = lscpu_regex.match(line)
        if m:
            var   = m.group(1)
            value = m.group(2)
            if var == 'CPU(s)':
                cpu_number = int(value)
            elif var == 'Model name':
                cpu_model = value

    if cpu_number and cpu_model:
        config['cpu_number'] = cpu_number

        m = re.search(r" (\w\d-\S+) ", cpu_model)
        if m:
            config['cpu_model'] = m.group(1)
        else:
            config['cpu_model'] = cpu_model

        return True
    else:
        return False

def storage_info():
    # Matches something like "md5    9:5    0 159,9G  0 raid1 /home"
    # <device>    <???>    <removable bit> <size>  ? <???> <mountpoint>
    lsblk_regex = re.compile(r'(\S+)\s+\S+\s+([01])\s+(\S+)\s+[01]\s+\S+\s+(\S+)?')
    config['disks']       = []
    config['filesystems'] = []

    try:
        output = subprocess.check_output(["lsblk", "-l"]).decode('utf-8')
    except FileNotFoundError:
        print('lsblk not found :O', file=sys.stderr)
        return False
    except subprocess.CalledProcessError:
        print('lsblk blew up :(', file=sys.stderr)
        return False

    lines = output.split('\n')
    for line in lines:
        m = lsblk_regex.match(line)
        if m:
            device     = m.group(1)
            removable  = m.group(2) == '1'
            size       = m.group(3)
            mountpoint = m.group(4)

            if removable or mountpoint == '[SWAP]':
                continue

            if re.match("sd[a-z]$", device):
                config['disks'].append(device)

            else:
                m = re.match("(nvme[0-9]n[0-9])$", device)
                if m:
                    config['disks'].append(m[1])

            if mountpoint and mountpoint not in config['filesystems']:
                config['filesystems'].append(mountpoint)

    return len(config['disks']) > 1 and len(config['filesystems']) > 1

def network_info():
    # matches something like '2: lan0    inet ...'
    ipaddr_regex = re.compile(r'\d+: (\S+)\s+inet ')
    config['interfaces'] = []

    try:
        output = subprocess.check_output(["ip", "-o", "address"]).decode('utf-8')
    except FileNotFoundError:
        print('ip not found :O', file=sys.stderr)
        return False
    except subprocess.CalledProcessError:
        print('ip blew up :(', file=sys.stderr)
        return False

    lines = output.split('\n')
    for line in lines:
        m = ipaddr_regex.match(line)
        if m:
            interface = m.group(1)
            if interface != 'lo' and interface not in config['interfaces']:
                config['interfaces'].append(interface)

    return len(config['interfaces']) > 0

if __name__ == "__main__":

    DEFAULT_CONFIG = 'config.py'

    if len(sys.argv) > 1:
        config_file_path = sys.argv[1]
    else:
        config_file_path = None

    config = {
        'debug': False,
        'font_size': 8,
        'swap': False,
        'torrents_host': None,
        'template': 'conkyrc-template'
    }

    if not cpu_info():
        config['cpu_number'] = 1
        config['cpu_model']  = ' '

    ram_info()

    if not storage_info():
        config['disks']       = ['sda']
        config['filesystems'] = ['/']

    if not network_info():
        config['interfaces'] = []

    if config_file_path:
        if os.path.exists(config_file_path):
            config_file_path = os.path.abspath(config_file_path)
        else:
            sys.exit('Could not access "%s"' % (config_file_path))

    elif os.path.exists(DEFAULT_CONFIG):
        config_file_path = os.path.abspath(DEFAULT_CONFIG)

    else:
        config_file_path = os.path.join(os.environ['HOME'], '.conky', DEFAULT_CONFIG)
        if not os.path.exists(config_file_path):
            sys.exit('Could not find the config file')

    print('Config file: %s' % (config_file_path), file=sys.stderr)

    with open(config_file_path) as f:
        code = compile(f.read(), 'config.py', 'exec')
        exec(code)

    if os.path.exists(config['template']):
            DIR = os.path.dirname(config['template'])
            if not DIR:
                DIR = os.getcwd()
    else:
        DIR = os.path.dirname(config_file_path)
        if not os.path.exists(os.path.join(DIR, config['template'])):
            sys.exit('Could not find the template file')

    print('Template file: %s' % (os.path.join(DIR, config['template'])), file=sys.stderr)

    env = Environment(loader=FileSystemLoader(DIR), trim_blocks=True, lstrip_blocks=True)

    template = env.get_template(os.path.basename(config['template']))

    out = template.render(config=config)
    print(out)
