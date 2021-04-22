# integration_iregul

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

_Component to integrate with [integration_iregul][integration_iregul]._

**This component will set up the following platforms.**

| Platform        | Description                       |
| --------------- | --------------------------------- |
| `binary_sensor` | Show something `True` or `False`. |
| `sensor`        | Show info from iregul API.        |

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `integration_iregul`.
4. Download _all_ the files from the `custom_components/integration_iregul/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "IRegul"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/integration_iregul/translations/en.json
custom_components/integration_iregul/translations/fr.json
custom_components/integration_iregul/__init__.py
custom_components/integration_iregul/binary_sensor.py
custom_components/integration_iregul/config_flow.py
custom_components/integration_iregul/const.py
custom_components/integration_iregul/manifest.json
custom_components/integration_iregul/sensor.py

```

## Configuration is done in the UI

<!---->

## Contributions are welcome

---

[integration_iregul]: https://github.com/PoppyPop/integration_iregul
[commits-shield]: https://img.shields.io/github/commit-activity/y/poppypop/integration_iregul.svg?style=for-the-badge
[commits]: https://github.com/PoppyPop/integration_iregul/commits/main
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/poppypop/integration_iregul.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/poppypop/integration_iregul.svg?style=for-the-badge
[releases]: https://github.com/PoppyPop/integration_iregul/releases
