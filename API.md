# Get power limit and mode

A command to get the power limit and the power mode is: ***get\_user\_power\_limit***. A response to this command is JSON with following fields:

* *powerMode* - a case sensitive string which describes the device performance mode. Possible values:
  + Low;
  + Normal;
  + High.
* *powerLimit* - an integer which stands for a user power limit (not the value from overclock tab).

# Set power limit and mode

A command to set the power limit and the mode is: ***set\_user\_power\_limit***. This command must include a payload. Example: *{"softRestart":true,"powerMode":1,"powerLimit":1000}*.

Fields are:

* *powerMode* - a case insensitive string or integer which describes a performance mode of the device. Possible values:
  + Low;
  + Normal;
  + High.
* *powerLimit* - an integer which stands for a user power limit (not the value from overclock tab).
* *softRestart* - a boolean which describes whether the device must try to set overclock parameters without stopping a mining[[1]](#footnote-1). Possible values:
  + true - try to set parameters without stopping a mining.
  + false - do not try to set parameters without stopping a mining.

The response to this command is API command status.

# Get fan mode and manual mode speed

A command to get the fan mode and the manual mode speed is: ***get\_fan\_mode***. A response to this command is JSON with following fields:

* *fan\_mode* - a string which describes the device fan mode. Possible values:
  + *auto* - the device will select fan speed based on its current state.
  + *manual* - the device will always use the selected fan speed.
* *manual\_fan\_speed\_percent* - an integer (percents) which describes the speed of fans. This field is taken into account only if *fan\_mode* is *manual*. Minimum value is 10 and maximum is 100.

# Set fan mode and manual mode speed

A command to set the fan mode and the manual mode speed is: ***set\_fan\_mode***. This command must include a payload. Example: *{"fan\_mode":"auto","manual\_fan\_speed\_percent":"93"}*.

Fields are:

* *fan\_mode* - a case sensitive string which describes the device fan mode. Possible values:
  + *auto* - the device will select fan speed based on its current state.
  + *manual* - the device will always use the selected fan speed.
* *manual\_fan\_speed\_percent* - an integer(percents) which describes speed of fans on startup. This field is taken into account only if *fan\_mode* is Manual. Minimum value is 10 and maximum is 100.
* The response to this command is API command status.

# Get overclock info

A command to get the overclock info is: ***get\_overclock\_info***. A response to this command is JSON with all overclock info.

The meaning of the most useful fields can be looked up in the overclock info json section of the appendix.

# Set overclock info

A command to set the overclock info is: ***set\_overclock\_info***. This command must include a payload. Example: *{"board\_temp\_target":74, "freq\_target":430, "power\_limit":3850, "voltage\_target":1420, "power\_max":3950, "voltage\_limit":1470, "voltage\_min":1300, "soft\_restart":true}*.

The meaning of the most useful fields can be looked up in the overclock info json section of the appendix.

The response to this command is API command status.

# Delete overclock info

A command to delete the overclock info is: ***delete\_overclock\_info***.

The response to this command is API command status.

# Get board slots state

A command to get the board slots states is: ***get\_board\_slots\_state***. A response to this command is JSON with following field:

* *auto\_disable* - a boolean value which describes whether to reboot the device on any board error in an attempt to recover it, or disable the board if recovery limit exceeded and 54x ("Chip id read error") persists.
* *failed\_to\_power\_on\_hashboard\_reboots* - an integer value which describes how many reboots were performed in an attempt to repair boards.
* *failed\_to\_power\_on\_hashboard\_max\_reboots* - an integer value which describes a limit of the recovery reboots.
* *limit\_boards\_power* - a boolean value which describes whether to use power from disabled or not working boards. Possible value:
  + *true* - do not use power from disabled or not working boards. The device will limit power of each board to the power it would get if the factory number of boards would be working and each board would get an equal share of the power.
  + *false* - use power from disabled or not working boards. The rest of the boards will get more power.
* *enabled* - an array of booleans. Each value describes the state of the corresponding board slot.
* *auto\_disabled* - an array of JSON objects. One object per disabled board. Each object describes the reason and time of disabling a board. Array indexes correspond to board indexes. Fields are:
  + *reason* - an integer field which describes error code which is a reason the board is disabled.
  + *time* - an integer value which describes a time when the board was disabled. The format is Unix timestamp.

# Set board slots state

A command to set the board slots states is: ***set\_board\_slots\_state***. This command must include a payload. Example: *{"auto\_disable":true, "failed\_to\_power\_on\_hashboard\_reboots":0, "failed\_to\_power\_on\_hashboard\_max\_reboots":5, "limit\_boards\_power": false, "enabled":[true, true, true, false]}*.

Field is:

* *auto\_disable* - a boolean value which describes whether to reboot the device on any board error in an attempt to recover it, or disable the board if recovery limit exceeded and 54x ("Chip id read error") persists.
* *failed\_to\_power\_on\_hashboard\_reboots* - an integer value which describes how many reboots were performed in an attempt to repair boards.
* *failed\_to\_power\_on\_hashboard\_max\_reboots* - an integer value which describes a limit of the recovery reboots.
* *limit\_boards\_power* - a boolean value which describes whether to use power from disabled or not working boards. Possible value:
  + *true* - do not use power from disabled or not working boards. The device will limit power of each board to the power it would get if the factory number of boards would be working and each board would get an equal share of the power.
  + *false* - use power from disabled or not working boards. The rest of the boards will get more power.
* *enabled* - an array of booleans. Each value describes the state of the corresponding board slot. The field is optional. If the array is empty it will enable all boards. Thus *"enabled":[]* is the same as *"enabled":[true, true, true, true]*.

# Reset recovery reboot counter

A command to reset the recovery reboot counter is: **reset\_failed\_to\_power\_on\_hashboard\_reboots**.

The response to this command is API command status.

# Get firmware version

A command to get the overclock info is: ***get\_firmware\_version***. A response to this command is JSON with following fields:

* *custom\_version* - a string which describes the device custom version.
* *firmware\_version* - a string which describes the device firmware version.

# Set boards cool fan percent

A command to set pwm% of the fans on cool down (Startup Cooling Fan Speed %) is: ***set\_boards\_cool\_fan\_percent***. This command must include a payload. Example: *{"boards\_cool\_fan\_percent":"30"}*.

Field is:

* *boards\_cool\_fan\_percent* - a string representing integer value which describes how much PWM to set on cool down. Minimum value is 10 and maximum is 100.

The response to this command is API command status.

# Power status

A command to get whether a device is suspended or deep\_suspended is: **power\_status**. A response to this command is JSON with following fields:

* *suspend* - a string which describes whether the device is suspended. Possible values:
  + true - string which means that device is suspended.
  + false - string which means that device is not suspended.
* *deep\_suspend*[[2]](#footnote-2) - a string which describes whether the device is deep\_suspended. Possible values:
  + true - string which means that device is deep\_suspended.
  + false - string which means that device is not deep\_suspended.

# Deep power off

A command to suspend the mining is: **deep\_power\_off**. An effect of this command will hold after reboot.

The response to this command is API command status.

# Deep power on

A command to resume the mining after *deep\_power\_off* command is: **deep\_power\_on**.

The response to this command is API command status.

# Delete upfreq result

A command to delete autotune (upfreq) results is: **delete\_upfreq\_results**.

The response to this command is API command status.

# Get cool temp

A command to get a temperature to which the device will cool down is: **get\_cool\_temp**. A response to this command is JSON with following fields:

* *type* - a string field which describes what cooling temperature will use the device. Possible values:
  + *default* - use the default cooling temperature of the device.
  + *env\_temp* - use an environment temperature.
  + *manual* - use the *manual\_temp* field value.
* *manual\_temp* - an integer field which describes a temperature to which the device will cool down.

# Set cool temp

A command to set a temperature to which the device will cool down is: **set\_cool\_temp**. This command must include a payload. Example: *{"type":"manual", "manual\_temp":35}*.

Fields are:

* *type* - a string field which describes what cooling temperature will use the device. Possible values:
  + *default* - use the default cooling temperature of the device.
  + *env\_temp* - use an environment temperature.
  + *manual* - use the *manual\_temp* field value.
* *manual\_temp* - an integer field which describes a temperature to which the device will cool down. Note that this value must be passed even if the *type* is not *manual*.

The response to this command is API command status.

# Get environment temperature limit

A command to get an environment temperature limit is: **get\_env\_temp\_limit**. A response to this command is JSON with following fields:

* *enabled* - a boolean value which describes whether the device must resume or suspend its work when *resume\_env\_temp* or *suspend\_env\_temp* are respectively reached.
* *resume\_env\_temp* - a string which describes an environment temperature when the device will start mining, if it was suspended due to too high environment temperature.
* *suspend\_env\_temp* - a string which describes an environment temperature when the device will stop mining.

# Set environment temperature limit

A command to set environment temperature suspend and resume temperatures is: **set\_env\_temp\_limit**. This command must include a payload. Example: *{"enabled": "true", "resume\_env\_temp": "50", "suspend\_env\_temp": "65"}*.

Fields are:

* *enabled* - a boolean value which describes whether the device must resume or suspend its work when *resume\_env\_temp* or *suspend\_env\_temp* are respectively reached.
* *resume\_env\_temp* - a string which describes an environment temperature when the device will start mining, if it was suspended due to too high environment temperature.
* *suspend\_env\_temp* - a string which describes an environment temperature when the device will stop mining.

Note that *resume\_env\_temp* must not be greater or equal to *suspend\_env\_temp.* The response to this command is API command status.

# Install AMS

A command to install the AMS is: **ams\_install**. This command must include a payload. Example: *{"api\_key":"517a56aa-a252-4a7a-9978-a76089aa2a5a", "update\_interval": 10}*.

Field is:

* *api\_key* - a string which is the AMS API key.
* *update\_interval* - an integer value which describes an interval (seconds) between send of the device data to the AMS server. The default value is 5. The value is optional, if no interval specified the 5 seconds will be applied.

The response to this command is API command status.

# Uninstall AMS

A command to uninstall the AMS is: **ams\_uninstall**.

The response to this command is API command status.

# Get AMS API key

A command to get the AMS API key is: **get\_ams\_install\_data**. A response to this command is JSON with following fields:

* *api\_key* - string which represents the AMS APIkey if any.
* installed - string which describes whether the AMS is installed. Possible values:
  + true - string which means that AMS is installed. The *api\_key* field will return the AMS API key.
  + false - string which means that AMS is not installed. The *api\_key* field will be an empty string.

# Get upfreq save params

A command to get an upfreq save params is: **get\_upfreq\_save\_params**. To get an explanation of the upfreq restore algorithm read a dedicated appendix 2. A response to this command is JSON with following fields:

* *freq\_delay\_air* - a string which describes a delay between iterations of changing of freq for an air cooling device. The smaller the delay the faster the tuning.
* *freq\_delay\_liquid* - a string which describes a delay between iterations of changing of the freq for a liquid cooling device. The smaller the delay the faster the tuning.
* *freq\_delay\_air\_default* - a string which describes the default value of *freq\_delay\_air*.
* *freq\_delay\_liquid\_default* - a string which describes the default value of *freq\_delay\_liquid*.
* *voltage\_offset\_air* - a string which describes a voltage change (mV) for an air cooling device. The value can be negative to down a voltage.
* *voltage\_offset\_liquid* - a string which describes a voltage change (mV) for a liquid cooling device. The value can be negative to down a voltage.
* *voltage\_offset\_air\_default* - a string which describes the default value of *voltage\_offset\_air*.
* *voltage\_offset\_liquid\_default* - a string which describes the default value of *voltage\_offset\_liquid*.
* *decrease\_voltage\_power\_limit\_tolerance\_percent* - a string which describes a value for which the limit can be exceeded by upfreq restore. When the upfreq restore is starting the first thing to do is to raise the frequency. After this the device will wait for stabilisation of temperature. This limit applies at this moment for voltage and power.
* *decrease\_voltage\_power\_limit\_tolerance\_percent\_default* - a string which describes the default value of *decrease\_voltage\_power\_limit\_tolerance\_percent*.
* *power\_limit\_tolerance\_percent* - a string which describes a value for which the power limit can be exceeded on upfreq restore.
* *power\_limit\_tolerance\_percent\_default* - a string which describes the default value of *power\_limit\_tolerance\_percent*.
* *iin\_limit\_tolerance\_percent* - a string which describes a value for which the inn limit can be exceeded on upfreq restore.
* *iin\_limit\_tolerance\_percent\_default* - a string which describes the default value of *iin\_limit\_tolerance\_percent*.
* *iout\_limit\_tolerance\_percent* - a string which describes a value for which the iout limit can be exceeded on upfreq restore.
* *iout\_limit\_tolerance\_percent\_default* - a string which describes the default value of *iout\_limit\_tolerance\_percent*.

# Set upfreq save params

A command to set an upfreq save params is: **set\_upfreq\_save\_params**. To get an explanation of the upfreq restore algorithm read a dedicated appendix 2. This command must include a payload. Example: *{"freq\_delay\_air":"2.337","freq\_delay\_liquid":"2.322","voltage\_offset\_air":"-22","voltage\_offset\_liquid":"0","decrease\_voltage\_power\_limit\_tolerance\_percent":"1.30","power\_limit\_tolerance\_percent": "2.6", "iin\_limit\_tolerance\_percent": "2.4","iout\_limit\_tolerance\_percent": "2.65"}*.

Fields are:

* *freq\_delay\_air* - a string which describes a delay between iterations of changing of freq for an air cooling device. The smaller the delay the faster the tuning.
* *freq\_delay\_liquid* - a string which describes a delay between iterations of changing of frequency for a liquid cooling device. The smaller the delay the faster the tuning.
* *voltage\_offset\_air* - a string which describes a voltage change (mV) for an air cooling device. The value can be negative to down a voltage.
* *voltage\_offset\_liquid* - a string which describes a voltage change (mV) for a liquid cooling device. The value can be negative to down a voltage.
* *decrease\_voltage\_power\_limit\_tolerance\_percent* - a string which describes a value for which the limit can be exceeded on the decrease of the voltage and power on upfreq restore.
* *power\_limit\_tolerance\_percent* - a string which describes a value for which the power limit can be exceeded on upfreq restore.
* *iin\_limit\_tolerance\_percent* - a string which describes a value for which the inn limit can be exceeded on upfreq restore.
* *iout\_limit\_tolerance\_percent* - a string which describes a value for which the iout limit can be exceeded on upfreq restore.

The response to this command is API command status.

# Start profiles generation

A command to start profiles generation is: **generate\_profiles**.

The response to this command is API command status.

# Stop profiles generation

A command to stop profiles generation is: **stop\_profiles\_generation**.

The response to this command is API command status.

# Get profiles generation status

A command to get the profiles generation status is: **get\_profiles\_generation\_status**. A response to this command is JSON with following fields:

* *generating\_profiles* - a string which describes whether profile generation is currently underway. Possible values:
  + *"true"* - generation is underway.
  + *"false"* - generation is not underway.
* *has\_generated\_profiles* - a string which describes whether the device has generated profiles. Possible values:
  + *"true"* - the device has generated profiles.
  + *"false"* - the device has not generated profiles.

# Delete generated profiles

A command to stop profiles generation is: **delete\_generated\_profiles**.

The response to this command is API command status.

# Get Profile Switcher

A command to get the profiles switcher settings is: **get\_profile\_switcher**. A response to this command is JSON with following fields:

* *enabled* - a string which describes whether profile generation is currently underway. Possible values:
  + *"true"* - generation is underway.
  + *"false"* - generation is not underway.
* *lower\_temp* - a string which describes the temperature celsius upon reaching which the device will select a lower profile.
* *raise\_temp* - a string which describes the temperature celsius upon reaching which the device will select a higher profile.
* *max\_profile\_id* - a string which describes an ID of profile which is the highest profile that could be set by the switcher system.
* *ignore\_pwm* - an integer field which describes whether the switcher will ignore current PWM when increasing profile. Possible values:
  + *true* - ignore PWM when increasing profile.
  + *false* - do not increase profile if PWM is >= 90%.
* *profiles* - a JSON array which contains JSON objects. Each object contains data about profiles. It has following fields:
  + *id* - an integer field which contains profile id. The one which could be set to *max\_profile\_id*.
  + *name* - a string field which contains the profile name.

# Set Profile Switcher

A command to set the profiles switcher settings is: **set\_profile\_switcher**. This command must include a payload. Example: {"enabled":"true","lower\_temp":"100","raise\_temp":"90","ignore\_pwm":"false","max\_profile\_id":"1000000"}.

Fields are:

* *enabled* - a string which describes whether profile generation is currently underway. Possible values:
  + *"true"* - generation is underway.
  + *"false"* - generation is not underway.
* *lower\_temp* - a string which describes the temperature celsius upon reaching which the device will select a lower profile.
* *raise\_temp* - a string which describes the temperature celsius upon reaching which the device will select a higher profile.
* *max\_profile\_id* - a string which describes an ID of profile which is the highest profile that could be set by the switcher system.
* *ignore\_pwm* - an integer field which describes whether the switcher will ignore current PWM when increasing profile. Possible values:
  + *true* - ignore PWM when increasing profile.
  + *false* - do not increase profile if PWM is >= 90%.

Note that *lower\_temp* must be greater than *raise\_temp.* The profile switcher can work only with generated profiles.The response to this command is API command status.

# Get stats

A command to get an api stats info is: **stats**. A response to this command is a JSON array which contains JSON objects. Each object contains data on the corresponding chain.

# Check upfreq results

A command to see whether upfreq results exist is: **has\_upfreq\_results**. A response to this command is JSON with following fields:

* *has\_upfreq\_results* - a string which describes whether upfreq results exist.

# Enable/disable power fan

A command to enable or disable the power fan is: **set\_psu\_fan**. This command must include a payload. Example: *set\_psu\_fan {"enabled": "true"}*.

Fields are:

* *enabled* - string which describes whether the psu fan must be enabled or disabled. Possible values:
  + *"true"* - enable psu fan.
  + *"false"* - disable psu fan.

The response to this command is API command status.

# Get liquid cooling

A command to get whether the device is in the liquid cooling mode is: **get\_liquid\_cooling**. A response to this command is JSON with following fields:

* *liquid\_cooling* - string which describes whether the device is in liquid cooling mode or not. Possible values:
  + *"true"* - the device is in liquid cooling mode.
  + *"false"* - the device is not in liquid cooling mode.
* *is\_fan\_machine* - string which describes whether the device is a fan cooling device. Possible values:
  + *"true"* - the device is a fan cooling device.
  + *"false"* - the device is not a fan cooling device.
* *cool\_mode* - string which describes the cooling mode of the device. Possible values:
  + *"air"* - the mode for devices which are cooled by fans.
  + *"liquid"* - the mode for devices which are cooled by immersion, but is not factory made for this.
  + *"hydro"* - the mode for devices which are cooled by a liquid cooling system.
  + *"immersion"* - the mode for devices which are factory made to be cooled by immersion.

# Set liquid cooling

A command to set the cooling mode is: **set\_liquid\_cooling**. This command must include a payload. Example: *set\_liquid\_cooling {"liquid\_cooling": "true"}*.

Fields are:

* *liquid\_cooling* - string which describes whether the device is in liquid cooling mode or not. Possible values:
  + *"true"* - the device is in liquid cooling mode.
  + *"false"* - the device is not in liquid cooling mode.

The response to this command is API command status.

# Get lower profile if autotune failed policy

A command to see whether the device will lower profile if autotune fails is: **get\_lower\_profile\_if\_autotune\_failed**. A response to this command is JSON with following fields:

* *enabled* - string which describes whether the device will lower profile if autotune fails. Possible values:
  + *"true"* - the device will lower profile if autotune fails.
  + *"false"* - the device will not lower profile if autotune fails.

# Set lower profile if autotune failed policy

A command to set whether the device will lower profile if autotune fails is: **set\_lower\_profile\_if\_autotune\_failed**. This command must include a payload. Example: *set\_lower\_profile\_if\_autotune\_failed {"enabled": "true"}*.

Fields are:

* *enabled* - string which describes whether the device will lower profile if autotune fails. Possible values:
  + *"true"* - the device will lower profile if autotune fails.
  + *"false"* - the device will not lower profile if autotune fails.

The response to this command is API command status.

# Get additional PSU status

A command to see whether the device has an additional PSU enabled is: **get\_additional\_psu**. A response to this command is JSON with following fields:

* *enabled* - string which describes whether the device has an additional PSU enabled. Possible values:
  + *"true"* - the device has an additional PSU enabled.
  + *"false"* - the device does not have an additional PSU enabled.

# Set additional PSU status

A command to set whether the device has an additional PSU enabled is: **set\_additional\_psu**. This command must include a payload. Example: *set\_additional\_psu {"enabled": "true"}*.

Fields are:

* *enabled* - string which describes whether the device has an additional PSU enabled. Possible values:
  + *"true"* - the device has an additional PSU enabled.
  + *"false"* - the device does not have an additional PSU enabled.

The response to this command is API command status.

# Upgrade PSU firmware

A command to upgrade PSU firmware is: **upgrade\_psu\_firmware**. Example: *upgrade\_psu\_firmware*.

The response to this command is API command status.

# Get list of allowed pools

A command to get a list of pools which are allowed to work with is: **get\_allowed\_pools**. A response to this command is JSON with following fields:

* *pools* - a JSON array which contains up to 10 strings. Each string contains a URL of the pool which is allowed to work with or empty.

# Set list of allowed pools

A command to set a list of pools which are allowed to work with is: **set\_allowed\_pools**. This command must include a payload. Example: *set\_allowed\_pools {"pools":["stratum+tcp://example.com:3333", "stratum+tcp://example.com:443"]}*.

Fields are:

* *pools* - a JSON array which can contain up to 10 strings. Each string must be a single url of the pool which is allowed to work with. Leave empty to remove a pool at the index.

The response to this command is API command status.

# Get stratum off

A command to get whether the stratum off is enabled is: **get\_stratum\_off**. A response to this command is JSON with following fields:

* *enabled* - string which describes whether the stratum off is enabled. Possible values:
  + *"true"* - the stratum off is enabled.
  + *"false"* - the stratum off is disabled.
* *stratum\_off\_server* - string which describes the stratum off server. That is IP plus port. Example: 192.168.1.1:9999.
* *stratum\_off\_user* - a string which describes the stratum off user name.
* *stratum\_off\_pass* - a string which describes the stratum off password.

# Set stratum off

A command to set the stratum off is: **set\_stratum\_off**. This command must include a payload. Example: *set\_stratum\_off {"enabled":true,"stratum\_off\_server":"192.168.1.1:9999","stratum\_off\_user":"stratumoff.user","stratum\_off\_pass":"123"}*.

Fields are:

* *enabled* - string which describes whether the stratum off is enabled. Possible values:
  + *"true"* - the stratum off is enabled.
  + *"false"* - the stratum off is disabled.
* *stratum\_off\_server* - string which describes the stratum off server. That is IP plus port. Example: 192.168.1.1:9999.
* *stratum\_off\_user* - a string which describes the stratum off user name.
* *stratum\_off\_pass* - a string which describes the stratum off password.

The response to this command is API command status.

# Get proxy info

A command to get the proxy info is: **get\_proxy\_info**. A response to this command is JSON with following fields:

* *enabled* - string which describes whether the traffic is routed through proxy. Possible values:
  + *"true"* - the traffic is routed through proxy.
  + *"false"* - the traffic is not routed through proxy.
* *host* - string which describes a proxy address.
* *user* - string which describes a proxy username.
* *password* - string which describes a proxy password.

# Set proxy info

A command to set the proxy info is: **set\_proxy\_info**. This command must include a payload. Example: *set\_proxy\_info {"enabled":"true","host":"192.168.1.1:9999", "user": "proxy\_user", "password": "proxy\_password"}*.

Fields are:

* *enabled* - string which describes whether the traffic is routed through proxy. Possible values:
  + *"true"* - the traffic is routed through proxy.
  + *"false"* - the traffic is not routed through proxy.
* *host* - string which describes a proxy address. It must be in format ip:host. For example: 192.168.1.1:9999.
* *user* - string which describes a proxy username.
* *password* - string which describes a proxy password.

The response to this command is API command status.

# Get compute info

A command to get the compute info is: **get\_compute\_info**. A response to this command is JSON with following fields:

* *wmt\_port* - string which describes a port for Whatsminer Tool connection. Default value: 8889.

# Set compute info

A command to set the compute info is: **set\_compute\_info**. This command must include a payload. Example: *set\_compute\_info {"wmt\_port":"8888"}*.

Fields are:

* *wmt\_port* - string which describes a port for Whatsminer Tool connection. Default value: 8889.

This command will take effect only after reboot. However, the *wmt\_port* value will change immediately. The response to this command is API command status.

# Get generate profiles parameters (get\_generate\_profiles\_params)

A command to get the parameters of the profiles generation is: **get\_generate\_profiles\_params**. A response to this command is JSON with following fields:

* *power\_limit\_air* - string which describes a limit for power in air cooling mode.
* *power\_limit\_liquid* - string which describes a limit for power in liquid cooling mode.
* *power\_limit\_hydro* - string which describes a limit for power for hydro devices.
* *power\_limit\_immersion* - string which describes a limit for power for immersion devices.
* *freq\_step* - string which describes an amount for which a frequency is adjusted per step.
* *power\_limit\_air\_default* - string which describes a default limit for power in air cooling mode.
* *power\_limit\_liquid\_default* - string which describes a default limit for power in liquid cooling mode.
* *power\_limit\_hydro\_default* - string which describes a default limit for power for hydro devices.
* *power\_limit\_immersion\_default* - string which describes a default limit for power for immersion devices.
* *freq\_step\_default* - string which describes a default amount for which a frequency is adjusted per step.

# Set generate profiles parameters (set\_generate\_profiles\_params)

A command to set the parameters of the profiles generation is: **set\_generate\_profiles\_params**. This command must include a payload. Example: *set\_generate\_profiles\_params {"power\_limit\_air":"3950","power\_limit\_liquid":"3950","power\_limit\_hydro":"10000","power\_limit\_immersion":"9000","freq\_step":"2.500000"}*.

Fields are:

* *power\_limit\_air* - string which describes a limit for power in air cooling mode.
* *power\_limit\_liquid* - string which describes a limit for power in liquid cooling mode.
* *power\_limit\_hydro* - string which describes a limit for power for hydro devices.
* *power\_limit\_immersion* - string which describes a limit for power for immersion devices.
* *freq\_step* - string which describes an amount for which a frequency is adjusted per step.

The response to this command is API command status.

# Get advanced fan mode (get\_advanced\_fan\_mode)

A command to get the advanced settings of the fans is: **get\_advanced\_fan\_mode**. A response to this command is JSON with following fields:

* *use\_chip\_temp* - a string which describes which temp the cooling system will use for its work. Possible values:
  + “true” - use chip temp when adjusting fans speed.
  + “false” - use board temp when adjusting fans speed.
* *use\_custom\_fan\_algo* - a string which describes whether to use the custom fan algorithms. That is an algorithm which utilises a PID controller mechanism. Possible values:
  + “*true*” - use a custom fan algorithm.
  + “*false*” - use standard fan algorithm.
* *use\_custom\_fan\_algo\_suspend* - a string which describes whether to use the custom fan algorithms while suspend mode. That is an algorithm which utilises a PID controller mechanism. Possible values:
  + “*true*” - use a custom fan algorithm.
  + “*false*” - use standard fan algorithm.
* *chip\_temp\_protect\_default* - a string which describes a maximum chip temperature. Usually the default value is 120°C.
* *chip\_temp\_target\_default* - a string which describes a target chip temp. By default this value is 5°C less than *chip\_temp\_protect\_default*.
* *adjust\_chip\_temp* - a string which describes an offset value which is added to themax chips temp. The device will try to keep max chip temp close to the *chip\_temp\_target\_default + adjust\_chip\_temp*. This value is respected only if *use\_chip\_temp* is *true*. This offset must be less or equal to 0.
* *adjust\_board\_temp* - a string which describes an offset value which is added to themax board temp.The device will try to keep max board temp close to the Board Target Temp + *adjust\_board\_temp*. This value is respected only if *use\_chip\_temp* is *false*. This offset must be less or equal to 0.
* *use\_target\_temp\_ramp* - a string which describes if use temp ramp on exit from suspend mode. Possible values:
  + “true” - use.
  + “false” - don’t use.
* *ramp\_adjust\_target\_temp* - a string which describes an offset value which is added to thecurrent target temp on exit from suspend mode, working only if *use\_target\_temp\_ramp* is “true”. This value must be in the range from -30.0 to 30.0.
* *ramp\_target\_temp\_speed* - a string which describes how fast the target temp rises after suspend mode, working only if *use\_target\_temp\_ramp* is “true”. This value is measured in degrees per second and must be in the range from 0.01 to 100.0.

Those settings do not survive reboot.

# Set advanced fan mode (set\_advanced\_fan\_mode)

A command to set the advanced settings of the fans is: **set\_advanced\_fan\_mode**. This command must include a payload. Example: *{"use\_chip\_temp":"false","use\_custom\_fan\_algo\_suspend":"false","use\_custom\_fan\_algo":"false","adjust\_chip\_temp":"0.000000","adjust\_board\_temp":"-0.000000","use\_target\_temp\_ramp":"false","ramp\_adjust\_target\_temp":"2","ramp\_target\_temp\_speed":"0.15"}*.

Fields are:

* *use\_chip\_temp* - a string which describes which temp the cooling system will use for its work. Possible values:
  + “*true*” - use chip temp when adjusting fans speed.
  + “*false*” - use board temp when adjusting fans speed.
* *use\_custom\_fan\_algo\_suspend* - a string which describes whether to use the custom fan algorithms while suspend mode. That is an algorithm which utilises a PID controller mechanism. Possible values:
  + “*true*” - use a custom fan algorithm.
  + “*false*” - use standard fan algorithm.
* *use\_custom\_fan\_algo* - a string which describes whether to use the custom fan algorithms. That is an algorithm which utilises a PID controller mechanism. Possible values:
  + “*true*” - use a custom fan algorithm.
  + “*false*” - use standard fan algorithm.
* *adjust\_chip\_temp* - a string which describes an offset value which is added to themax chips temp. The device will try to keep max chip temp close to the *chip\_temp\_target\_default + adjust\_chip\_temp*. This value is respected only if *use\_chip\_temp* is *true*. This offset must be less or equal to 0.
* *adjust\_board\_temp* - a string which describes an offset value which is added to themax board temp.The device will try to keep max board temp close to the Board Target Temp + *adjust\_board\_temp*. This value is respected only if *use\_chip\_temp* is *false*. This offset must be less or equal to 0.
* *use\_target\_temp\_ramp* - a string which describes if use temp ramp on exit from suspend mode. Possible values:
  + “true” - use.
  + “false” - don’t use.
* *ramp\_adjust\_target\_temp* - a string which describes an offset value which is added to thecurrent target temp on exit from suspend mode, working only if *use\_target\_temp\_ramp* is “true”. This value must be in the range from -30.0 to 30.0.
* *ramp\_target\_temp\_speed* - a string which describes how fast the target temp rises after suspend mode, working only if *use\_target\_temp\_ramp* is “true”. This value is measured in degrees per second and must be in the range from 0.01 to 100.0.

The response to this command is API command status. Those settings do not survive reboot.

# Summary (summary)

A command to get the summary is **summary**. That is the factory command. However it has additional fields. Those fields are:

* *Power Realtime* - an integer field which describes a current power.
* *Miner Memory Usage* - an integer which describes an amount of memory used by the firmware. Unit: MB.
* *Miner PID* - an integer which describes the current PID of the firmware.
* *PSU Serial No* - a string field which describes a PSU serial number.
* *PSU Name* - a string field which describes a PSU model.
* *PSU Vin0* - a floating point field which describes an input voltage for 1st phase.
* *PSU Vin1* - a floating point field which describes an input voltage for 2nd phase. It is zero when supply is one-phase.
* *PSU Vin2* - a floating point field which describes an input voltage for 3rd phase. It is zero when supply is one-phase.
* *PSU Vout* - a floating point field which describes an output voltage.
* *PSU Iout* - a floating point field which describes an output current.
* *PSU Iin0* - a floating point field which describes an input current for the 1st phase.
* *PSU Iin1* - a floating point field which describes an input current for the 2nd phase. It is zero when supply is one-phase.
* *PSU Iin2* - a floating point field which describes an input current for the 3rd phase. It is zero when supply is one-phase.
* *Chip Temp Protect* - an integer value which describes a limit temperature for chips.
* *Chip Temp Target* - an integer value which describes a target temperature for chips.
* *PSU Temp0* - a floating point field which describes a PSU temperature from the 1st sensor.
* *PSU Temp1* - a floating point field which describes a PSU temperature from the 2nd sensor.
* *PSU Temp2* - a floating point field which describes a PSU temperature from the 3rd sensor.
* *PSU Fan Speed* - an integer field which describes a speed of the PSU fan.
* *Status* - a string field which describes the current status of the device. Possible states:
  + *Suspended: High Env. Temp* - the device is suspended due to too high environment temperature.
  + *Suspended* - the device is suspended.
  + *Generating Profiles* - the device is generating profiles.
  + *Restoring* - the device sets a profile from saved results.
  + *Tuning* - the device is tuning a profile.
    *Miner Type* - a string field which describes a model of the device.
* *Factory GHS* - an integer field which describes a hashrate of the device with the factory settings. Unit: GH/s.

# Reset MAC address (reset\_mac)

A command to set the MAC address to a new value is: **reset\_mac**. This command does not require a payload. In such a case the MAC address will be generated automatically. However, an optional argument *mac* is accepted. Example: *{"mac":"C8:11:05:00:53:3A"}*.

Fields are:

* *mac* - a string which describes a MAC address to set.

The response to this command is API command status.

# Changelog

## 2.0.2

Add commands *get\_debug\_options* and *set\_debug\_options*.

## 2.0.3

Fix a bug with a cutted down response of devs command on devices with a huge number of chips.

#

# Appendix 1

## Overclock info JSON

This JSON contains all overclock info. Among others, this JSON will include following fields:

1. *board\_temp\_target* - an integer which describes boards target temperature of the device.
2. *freq\_target* - an integer which describes a target frequency of the device.
3. *power\_limit* - an integer which describes a power limit of the device. This value must be less than powerMax.
4. *voltage\_target* - an integer which describes a target voltage of the device. This value must be less than voltageLimit and greater than voltageMin.
5. *power\_max* - an integer which describes a max power of the device. This value must be greater than powerLimit.
6. *voltage\_limit* - an integer which describes a voltage limit (maximum voltage) of the device. This value must be greater than VoltageMin and voltageTarget.
7. *voltage\_min* - an integer which describes a minimum voltage of the device. This value must be less than voltageLimit and voltageTarget
8. *soft\_restart* - a boolean which describes whether the device must try to set overclock parameters without stopping a mining[[3]](#footnote-3). This field can be passed to set commands, but it is never returned by get commands. Possible values:
   1. true - try to set parameters without stopping a mining.
   2. false - do not try to set parameters without stopping a mining.

The preconditions for the *sorf\_restart* to work is:

1. The current status of a device must be Mining.
2. There must be an upfreq result for the profile which is set by the command.
3. The feature works only for the enterprise version of the firmware.

Note that when this data is returned by the get\_overclock\_info command not all of those fields are on the same level. Some fields would be available under the *fields* field. Those fields are: *board\_temp\_target*, *freq\_target*, *power\_limit*, *voltage\_target*, *power\_max*, *voltage\_limit*, *voltage\_min*, *soft\_restart*. Also, those fields will be JSON objects. Each object will contain following fields:

*min* - a minimum value for the field.

*current* - a current value of the field.

*default* - a default value for the field.

*max* - a maximum value for the field.

## API command status

That are responses to commands which by their nature do not explicitly require any response. The response simply shows whether a particular command succeeded or not. Not exhaustive list of examples:

* Successful completion of a command:
  + *{"STATUS":"S","When":1723807869,"Code":131,"Msg"[[4]](#footnote-4):"API command OK","Description":""}*
* Unsuccessful completion of command:
  + *{"STATUS":"E","When":1723808069,"Code":132,"Msg":"API command ERROR","Description":""}*

Note that both above mentioned responses mean that the specified command does exist. When a command is unknown to the device it responds with the following message:

* *{"STATUS":"E","When":1723810620,"Code":14,"Msg":"invalid cmd","Description":""}*

#

# Appendix 2

## Upfreq restore algorithm

Upfreq restore procedure consists of 4 steps.

On the first step the device sets a voltage. The voltage to be set is selected by the device based on current environment temperature. Then the *voltage\_offset\_air* or *voltage\_offset\_liquid* is added to the voltage value. That is the final value which will be set.

On the second step the device raises frequency. It is done by a number of small frequency changes to make the process more safe. The delay between each step could be set via *freq\_delay\_air* and *freq\_delay\_liquid* fields of the **set\_upfreq\_save\_params** command.

On the third step the device waits for a temperature to become stable.

On the fourth step the device starts a fine tuning of the voltage. It selects a voltage which provides the closest hashrate to the specified.

1. The device can fail to do so. In such a case mining will be stopped even if the soft\_restart is set to true. [↑](#footnote-ref-1)
2. Deep suspend is a simple suspend but it holds after reboot. [↑](#footnote-ref-2)
3. The device can fail to do so. In such a case mining will be stopped even if the soft restart is set to true. [↑](#footnote-ref-3)
4. The "Msg" field can contain data which is a response of the command. [↑](#footnote-ref-4)
