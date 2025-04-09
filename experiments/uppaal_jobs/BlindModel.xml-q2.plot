set terminal epscairo
set output '../../BlindControl/experiments/uppaal_jobs/BlindModel.xml-q2.eps'
set title 'Simulations (1)'
set key outside center right enhanced Left reverse samplen 1
set grid xtics ytics lc rgb '#808080'
set xlabel 'time'
set ylabel 'value'
set style data points
set datafile separator ','
plot '../../BlindControl/experiments/uppaal_jobs/BlindModel.xml-q2-e0.csv' with lines lc rgb '#ff0000' title 'room_temp'
