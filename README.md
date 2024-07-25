# ha_fronius_set_service
Allows setting of fronius settings from HA (like battery charging schedule)

For now it just has one call to allow you to set how much your battery will charge (can charge at 9000 watts from the grid on my system!), but importantly it does handle all the login and things to you local Fronius inverter so with a few adjustments you can have it call all sorts of things on your inverter.  

This is tested with a Fronius Gen24 Symo. 




## Setup

First Copy the files from ```fronius_settings_service``` in to your custom_components folder under HA config.

Next create or edit ```secrets.yaml``` in the config root and add "fronius_password: <your password>".

In ```configuration.yaml``` add (and change to correct ip address):

```yaml
fronius_settings_service:
  password: !secret fronius_password
  base_url: http://192.168.1.66
  referer_url: http://192.168.1.66/
```


Restart HA, and you should be able to call the service. It has two parameters:

```power: 5000``` will set the battery to draw a minimum of 5kw at all times
```remove: true``` will cancel this and you can get on with your day :)

![image](https://github.com/user-attachments/assets/57d29b6c-18c3-4099-a5fd-6d052f548976)


![image](https://github.com/user-attachments/assets/5f8b7199-711c-4460-bb1a-f2f8ebad5d9b)
