# Watermeter Reporter

Watermeter Reporter is a Home Assistant custom integration for submitting water meter readings to the [Dobczyce](https://www.dobczyce.pl/woda) service.

![Watermeter Reporter logo](logo.svg)

## Features

- Exposes the `watermeter_reporter.submit_reading` service.
- Supports the main, secondary, and tertiary meter readings.
- Uses the reading date supplied by Home Assistant.
- Automatically solves the arithmetic CAPTCHA displayed by Dobczyce.
- Supports a dry-run mode for inspecting the generated submission payload.

## Installation

1. Open HACS in Home Assistant.
2. Select **Integrations** and choose **Add Repository**.
3. Enter the repository URL:

   ```text
   https://github.com/jkramarz/watermeter-reporter
   ```

4. Install **Watermeter Reporter** from HACS.
5. Restart Home Assistant.
6. Open **Settings → Devices & Services → Add Integration**, search for **Watermeter Reporter**, and select **Add**.
7. Open **Developer Tools → Services** and call `watermeter_reporter.submit_reading`.

## Service

Call `watermeter_reporter.submit_reading` from a script, automation, or action.

```yaml
service: watermeter_reporter.submit_reading
data:
  owner_name: "Jane Doe"
  address: "Main Street 1"
  meter_number: "M-42"
  primary_reading: 1234
  secondary_reading: 567
  tertiary_reading: 89
  reading_date: "2026-10-07"
  notes: "Meter changed"
```

The `meter_number`, secondary reading, tertiary reading, reading date, notes, and dry-run fields are optional. The reading date defaults to the current date, and `dry_run` defaults to `false`.

## Development

The integration uses `requests` and `beautifulsoup4`. Install the dependencies and run the unit tests:

```bash
python3 -m unittest discover -v
```
