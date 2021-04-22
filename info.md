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

{% if not installed %}

## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "IRegul".

{% endif %}

## Configuration is done in the UI

<!---->

---

[integration_iregul]: https://github.com/PoppyPop/integration_iregul
[commits-shield]: https://img.shields.io/github/commit-activity/y/poppypop/integration_iregul.svg?style=for-the-badge
[commits]: https://github.com/PoppyPop/integration_iregul/commits/main
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/poppypop/integration_iregul.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/poppypop/integration_iregul.svg?style=for-the-badge
[releases]: https://github.com/PoppyPop/integration_iregul/releases
