Code repo for analysis of 50 LV transformers in the UK.

Raw data was sourced from: https://opennetzero.org/dataset/lv-load-monitor-data

plot.py was run to convert this data into smaller CSVs (one week) for frontend visualisation (an original commit has code to generate graph .png's)

index.html is used to visualise about 500 charts. There's a separate chart for each cable (L1, L2, L3) for each feeder (of between 1-5 feeders), for 50 transformers. The code is hosted here: https://lv-data-analysis-jeromeminney.netlify.app/

Medium article describing the project more verbosely here: https://medium.com/@jeromeminney_34852/shifting-energy-consumption-meeting-net-zero-goals-at-a-street-level-5a47c9275dac