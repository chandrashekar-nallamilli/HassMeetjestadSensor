{% if prerelease %}
### NB!: This is a Beta version!
{% endif %}

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

# Meetjestad Sensor

This is a minimum implementation of an integration providing a sensor measurement.

Install is available using [HACS](https://github.com/custom-components/hacs) or you can install manually.

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `meejestad_sensor`.
4. Download _all_ the files from the `custom_components/meejestad_sensor/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
@All the parameters are required
Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
  - platform: meetjestad_sensor
    name: meetjestad
    station_id: [ YOUR_STATION_ID ]
    monitored_conditions:
      - temperature
      - humidity
```
