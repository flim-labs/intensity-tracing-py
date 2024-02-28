# Intensity Tracing Changelog

## Version 1.4

- Add download acquired data functionality

## Version 1.3

- Ring buffer adaptations and realtime improvements
- User can visualize cps value on charts

## Version 1.2

- Improve data processing and implement QTimer
- Recalibration of GUI parameters related to max points on the chart and draw frequency to prevent overload
- Max acquisition time value set to 1800s (30m)
- Update data handling and improve plot visual in tracing photons

## Version 1.1

- Add export/load parameters configuration functionality
- User can specify `time_span` parameter in order to control X axis range
- `max_points` automatically calculated depending on `bin_width`, `time_span` and `draw_frequency`
- Warning message system improvement

## Version 1.0

- UI/UX improvements
- GUI parameterization
- Reset parameters button added
- Free running and Fixed acquisition mode choice
- Bin width, Max points and acquisition time customization
- Plots of single-photon counts as a function of time
- Automatically set the correct firmware based on the connection channel selected (USB/SMA)
- UI errors handling improvements
- Export data functionality added
- Add `plot_data_file.py` script to analyze and plot exported data
- Add header and metadata information to the binary exported data
- GUI now has a link to the technical documentation for more info
