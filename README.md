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
speaker should be able to follow along. Here's an
example:

```
WHEN person.tom ARRIVES home
  IF sun IS DOWN
   THEN
     TURN ON porch.lights
     UNLOCK entry.doors
```

### Writability
There are very few syntactical rules to OttoScript.
White space, line breaks and capitalization are
are all ignored. (They do, however, make it easier
read). Dot notation (`person.tom`) is necessary
for specifying entities. In addition to supporting
standard HomeAssistant entities, OttoScript
supports rich area-based entity shorthand. In the
example above, `TURN ON porch.lights` will turn on
all the lights in the porch area.

### Scalability
OttoScript is designed to scale to highly complex
automations and offers features for power users
such as:
 - variable assignment ('set @color = 'red')
 - complex conditions ('if sun is down and porch.lights != 'on')
 - Advanced logic (CASE, FOR loops)
 - user-defined functions for frequently used code
 - Ability to call pyscript functions directly from OttoScripts


## Installation

## Usage
