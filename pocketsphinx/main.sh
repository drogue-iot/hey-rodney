#!/usr/bin/env bash

if [[ "$FORCE_ALSA" == "true" ]]; then
  # The only way to switch to ALSA is by letting `ad_pulse` fail to import
  rm -f /usr/local/lib/python3.8/dist-packages/sphinxbase/ad_pulse.py
fi

exec /hey-rodney/main.py "$@"
