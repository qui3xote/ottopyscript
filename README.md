# OttoScript

## What is OttoScript?
OttoScript is domain specific language (DSL) designed
to make writing HomeAssistant automations easier,
and more intuitive than existing options, while being
powerful enough to handle all but the most complex 
situations.

## Whatis OttoPYScript?
OttoPyScript is the interpreter layer that converts OttoScript commands into HomeAssitant commands (via the PyScript integration). You need both if you want to try OttoScript on HomeAssistant. (A simpler install process *will* be available before 1.0 release). 

## Installation
1. [Install Pyscript](https://github.com/custom-components/pyscript) by either HACS (preferred) or manual method. **Be sure to set `allow_all_imports: true` in your pyscript configuration.**
2. [Install ottoscript](https://github.com/qui3xote/ottoscript) in the `/config/` directory of your HA instance. You can download the folder or use git clone, but make sure the entirety of the repo is in /config/ottoscript/
3. Clone this repository into `/config/pyscript/apps/` (If this directory doesn't exist, you probably didn't reboot after install pyscript).


## Configuration
The OttoPyScript config (see config.yaml.sample) needs to be place included or copied directly into the `Apps:` section of the pyscript config (/config/pyscript/config.yaml). 

Options:
Directory - the path to your scripts directory in your HA instance (pick any place you like). OttoScript will run all files ending in .otto in that directory. (It will NOT check subdirectories).

Verbose: 0 or 1. Controls the amount of debugging info writing to the HA log. Leave this on 0 unless you're seeing an error you can't otherwise explain. 

area_shortcuts: a dictionary of lists. The keys are 'groups' and the items are HomeAssistant areas (or other groups). Best understood by looking at the sample file. These groups can be referenced like any other area in OttoScript.



## Usage
See the [ottoscript](https://github.com/qui3xote/ottoscript) repository for details on the language and writing automations.
