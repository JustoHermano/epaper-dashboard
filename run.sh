
. env.sh


#!/bin/bash

start_time=$(date +%s)
file="runningProgram.txt"

if [ -e "$file" ]; then
    echo "Program already running. Exiting."
    exit 1
fi


current_date=$(date '+%Y-%m-%d %H:%M:%S')
echo "Date: $current_date" >> "$file"

function log {
    echo "---------------------------------------"
    echo ${1^^}
    echo "---------------------------------------"
}

if [ $WAVESHARE_EPD75_VERSION = 1 ]; then
    export WAVESHARE_WIDTH=640
    export WAVESHARE_HEIGHT=384
else
    export WAVESHARE_WIDTH=800
    export WAVESHARE_HEIGHT=480
fi

if [ $PRIVACY_MODE = 1 ]; then
    log "Get XKCD comic strip"
    .venv/bin/python3 xkcd_get.py
    if [ $? -eq 0 ]; then
        .venv/bin/python3 display.py xkcd-comic-strip.png
    fi

else

    log "Add weather info"
    .venv/bin/python3 screen-weather-get.py

    log "Add Calendar info"
    .venv/bin/python3 screen-calendar-get.py

    # Only layout 5 shows a calendar, so save a few seconds.
    if [ "$SCREEN_LAYOUT" -eq 5 ]; then
        log "Add Calendar month"
        .venv/bin/python3 screen-calendar-month.py
    fi

    if [ -f screen-custom-get.py ]; then
        log "Add Custom data"
        .venv/bin/python3 screen-custom-get.py
    fi

    log "Export to PNG"
    .venv/bin/cairosvg -o screen-output.png -f png --dpi 300 --output-width $WAVESHARE_WIDTH --output-height $WAVESHARE_HEIGHT screen-output-weather.svg

    .venv/bin/python3 display.py screen-output.png
fi


rm "$file"

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Time taken: $duration seconds | Date: $current_date" >> time_log.txt
