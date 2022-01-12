# OttoScript

## What is OttoScript?
OttoScript is domain specific language (DSL) designed
to make writing HomeAssistant automations easier,
and more intuitive than existing options, while being
powerful enough to handle all but the most complex 
situations. It is built around 3 core principles:

### Readability
OttoScript uses simple words and minimal syntax so
that it reads like (almost) like English. Any native
speaker should be able to follow along. Here's a simple
example:

```
WHEN input_boolean.sleep CHANGES TO 'on'
  IF person.tom IS 'home'
   THEN
     TURN OFF lights.porch_sconce_lights
     LOCK lock.entry
  END
```

### Writability
There are very few syntactical rules to OttoScript.
White space, line breaks and capitalization are
are all ignored. (They do, however, make it easier
read). Dot notation (`person.tom`) is used to
specify entities, variables are prefixed with '@', 
and multiple scripts can be included in a single file 
by terminating each one with a semi-colon. 

_Future release_: In addition standard HomeAssistant entities, 
OttoScript will support area-based entity shorthand. For example,
`TURN ON porch.lights` will turn on all the lights in the porch area.

### Scalability
OttoScript is designed to scale to highly complex
automations and offers features for power users
such as:
- compound IF statements ('if sun is down and porch.lights != 'on')
- CASE Statement
- variable assignment ('set @color = 'red')

_Future Release_:
- Advanced logic (FOR loops)
- user-defined functions for frequently used code
- Ability to call pyscript functions directly from OttoScripts


## Installation
OttoScript has two parts: The language definitons and
execution logic [ottoscript](https://github.com/qui3xote/ottoscript) and an 
interpreter (this repo) that converts that logic into HASS commands, and 
relies on pyscript.

1. [Install Pyscript](https://github.com/custom-components/pyscript) by either HACS (preferred) or manual method. Be sure to set `allow_all_imports: true` in your pyscript configuration file.
2. [Install ottoscript](https://github.com/qui3xote/ottoscript) in the `/config/` directory of your HA instance.
3. Clone this repository into `/config/pyscript/apps/'
4. Create a directory to store your ottoscripts and add it to the pyscript configuration (see config.yaml.sample in this repo) - alternately, you can keep a seperate config.yaml in `/config/pyscript/app/ottopyscript` and include it in your pyscript config.

## Usage
Ottopyscript will import all `.otto` files in the specified directory (or directories) though it does not (currently) include sub-directories. All scripts in the file will be parsed and added as automations. See the [ottoscript](https://github.com/qui3xote/ottoscript) repository for details on the language.

## Current limitations
- Only state-based triggers are currently supported. Time-based and other trigger types will be added in a future release.
- If you change an otto script, you must reload pyscript before the change will take effect (from the HA interface, this is available in the Server Controls section).
- Only a small number of commands (turn on/off, toggle, lock/unlock) have been implemented so far.
