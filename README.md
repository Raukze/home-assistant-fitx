[![HACS Default][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]

[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Default&style=popout&color=green&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/default_repositories

[latest_release]: https://github.com/Raukze/home-assistant-fitx/releases/latest
[releases_shield]: https://img.shields.io/github/release/Raukze/home-assistant-fitx.svg?style=popout

[releases]: https://github.com/Raukze/home-assistant-fitx/releases
[downloads_total_shield]: https://img.shields.io/github/downloads/Raukze/home-assistant-fitx/total


# 🏋️ FitX Gym Utilization Rate Sensor

## Installation

<!--### HACS

This component is easiest installed using [HACS](https://github.com/custom-components/hacs). -->

### 🔧 Manual installation

Copy the `fitx` folder from `custom_components/` to the `custom_components/`directory inside your config Home Assistant directory.

## Configuration

### Configuration Variables

| Name | Type | Default | Description |
|---|---|---|---|
| id **(required)** | int | | Numerical id of the studio. See [Numeric ID](#numeric-id) |
| name | string | Name for `id` via API | Name of the FitX utilization rate sensor. |

### Example Configuration

So if the gym you want to track is https://www.fitx.de/fitnessstudios/bielefeld-mitte add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: fitx
    locations:
      - id: 1516366190
        name: Gym Bielefeld
```

### Sensor Attributes
- **id**: The `id` set in the config.
- **url**: The `URL` used for the web request.

### Numeric ID
Look at this [Gist](https://gist.github.com/JayReturns/0ca493e39a2eebf4c2434e0603dd9148) and run it with your FitX Studio Name to get the numeric ID.

#### Example
<img src="https://raw.githubusercontent.com/Raukze/home-assistant-fitx/main/screenshots/screenshot-example-sensor.png" width=50%>