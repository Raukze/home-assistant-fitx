[![HACS Default][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]

[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Default&style=popout&color=green&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/default_repositories

[latest_release]: https://github.com/Raukze/home-assistant-fitx/releases/latest
[releases_shield]: https://img.shields.io/github/release/Raukze/home-assistant-fitx.svg?style=popout

[releases]: https://github.com/Raukze/home-assistant-fitx/releases
[downloads_total_shield]: https://img.shields.io/github/downloads/Raukze/Raukze/home-assistant-fitx/total


# 🏋️ FitX Gym Usage Sensor

## Installation

<!--### HACS

This component is easiest installed using [HACS](https://github.com/custom-components/hacs). -->

### 🔧 Manual installation

Copy the `fitx` folder from `custom_components/` to the `custom_components/`directory inside your config Home Assistant directory.

## Configuration

### Configuration Variables

| Name | Type | Default | Description |
|---|---|---|---|
| id **(required)** | string | | Name of the gym from [here](https://www.fitx.de/fitnessstudios "FitX Locations"). You need the `id` part `https://www.fitx.de/fitnessstudios/{id}` |
| name | string | Value of `id` | Name of the FitX usage sensor. |

### Example Configuration

So if the gym you want to track is https://www.fitx.de/fitnessstudios/berlin-alexanderplatz add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: fitx
    locations:
      - id: berlin-alexanderplatz
        name: Gym Berlin
```

### Sensor Attributes
- **id**: The `id` set in the config.
- **url**: The `URL` used for the web request.
- **studioName**: The gym location's name
- **address**: The address of the gym.

#### Example
<img src="screenshots/screenshot-example-sensor.png" width="300">