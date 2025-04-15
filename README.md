# `th0xx`

Use you keyboard to play (platform) fighters.

## PLAN

- Linux:
  - Use the [`libevdev` API](https://www.freedesktop.org/software/libevdev/doc/latest/) to grab keyboard inputs.
  - Use the [Linux's `uinput` API]() to generate joystick device / outputs.
- Windows:
  - Use [Window's Raw Input API](https://learn.microsoft.com/en-us/windows/win32/inputdev/raw-input) to grab keyboard inputs.
  - Use [vjoy](https://sourceforge.net/projects/vjoystick/) to generate joystick device / outputs.
- MacOS: TODO / IDK
  - Can't really test because I don't have a Mac.
