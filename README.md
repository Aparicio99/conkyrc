# Conky config and scripts

## Contents
  * **conkyrc-generator.py** - Script to create a config based on a template and properties of the running system
  * **conkyrc-template** - Config jinja2 template
  * **config-example.py** - Example config file to conkyrc-generator
  * **ping.lua** - Lua script to show ping delay value and graph
  * **transmission-status.py** - Script to show transmission torrents status
  * **conkyrc-example** - Example generated conkyrc

### conkyrc-generator.py

Usage: `./conkyrc-generator.py > ~/.conkyrc`

Or

Usage: `./conkyrc-generator.py config.py > ~/.conkyrc`

The main purpose of the script is the generate a final conkyrc config based on a jinja2 template.

This approach has the following benefits compared with a static conkyrc:
  * Loops to dynamically write multiple identical lines, as is common on conkyrc configs.
  * Separate the conkyrc structure from the details of the running system.
  * Adapt the generated conkyrc to the running system, like number of CPUs, hard drives, etc.
  * Share the same template between different machines, with few or no changes to a separate config file.
  * Eliminates the need for lots of conditional statements in conkyrc that messes up the layout, just to support different systems.

It automatically gets the info from the running system to make available the following variables to the template:
  * config.**cpu_number** - Number of CPU cores
  * config.**cpu_model** - CPU model string from /proc/cpuinfo
  * config.**swap** - Boolean for swap space configured or not
  * config.**disks** - List of the non-removable hard-drives detected
  * config.**filesystems** - List of filesystems in non-removable disks
  * config.**interfaces** - List of network interfaces with IP and excluding the loopback interface

### conkyrc-template

Jinja2 conkyrc template to be used with the `conkyrc-generator.py`

The content of variables can be included by doing {{variable\_name}}.

The complete reference for the templating language can be found on the [Jinja website](http://jinja.pocoo.org/).

### config.py

This file is evaluated by the `conkyrc-generated` and can be used the override the automatic variables created,
or create new variables to include in the template.

The following variables are expected by the included `conkyrc-template`:
  * config.debug - Boolean to print debug information
  * torrents_host - Host where transmission-daemon is running, or None to exclude the torrents section

Since any python code can be included here, it can also be used to remove or add specific filesystems or disks to the generated arrays.

### Conky.ttf

TrueType font with symbols of hardware and other stuff to be used as headers of sections.

Create on https://glyphter.com/ and modified with [FontForge](http://fontforge.github.io/en-US/).

### ping.lua

Lua script to extend conky with new functions to show ping delay value and graph.

Print the numeric value: `${lua_parse router_ping_string}`

Print the graph of the value history: `${lua_graph router_ping 9,90 ff8c00 ff8c00}`

Must be included in the conkyrc with the line: `lua_load ~/.conky/ping.lua`

It reads the file /tmp/router\_status and expects one line containing something like `5.30 ms`.

This was designed to be used with my `pingrage` script [here](https://github.com/Aparicio99/scripts/blob/master/pingrate), which pings the desired host in a loop and outputs the delay to the file.

### transmission-status.py

Script that outputs the active torrents from a local or remote transmission-daemon.

The output contains color codes to be parsed by conky.

## conkyrc-example

Example of the conkyrc generated by the combination of the `conkyrc-generater.py`, `conkyrc-template` and `config-example.py` included here.
