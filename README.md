# msfs-h145-continuous-activator
Run this Python script to have the HPG Airbus H145 activated without needing to manually run ActivatorApp.exe every 2 hours.

In the event where you get the activation annunciator, hit ALT+S (Toggle alternate static) to force H145 to read the license file.

You do not need to provide the activation key to this application - it will read it from the activation directory. As such, you **must** have used the ActivatorApp.exe (successfully) at least once (the file `hpg-airbus-h145/HPGH145/keycode.txt` already exists).

## Quickstart

### Preparations

- Install [Python 3](https://www.python.org/downloads/), pick whichever is the latest (_3.5 is the oldest supported_).
  - If unsure, Choose "system" install (for all users).
  - Alternatively, [get from Microsoft store](https://www.microsoft.com/en-us/search?q=python).
- `python -m pip -q -q -q --no-input --disable-pip-version-check --no-python-version-warning install requests`

### Running the script

- `python [path to this directory]/h145.py`

## Troubleshooting

- ### H145 activation directory: "&lt;UNKNOWN&gt;"

`python [path to this directory]/h145.py --package [path to H145 directory (with ActivatorApp.exe)]`

- ### Activation annunciator does not go away

Please make sure this is your first flight after launching MSFS.
Under certain conditions, the Early Release H145 will not read the license file - activation via ActivatorApp.exe will not work, Toggle alternate static (simconnect or hotkey) will also do nothing. The only resolution is to restart MSFS.


