# BubbleSeparateApp


USE MY REPO https://github.com/MaheshUmale/App as BASE GUIDE 
AND CREATE NEW PROJECT WITH FOLLOWING LOGIC 
FEATURE 1) EXTARCT 
1)1) EXTRACT UPSTOX LOGIN LOGIC WITH PAGE
1)2) WSS streamer LOGIC TO SUBSCRIBE TO LIVE 'ltpc' feed of Instrument Keys
1)3) USE FILE BBSCAN_FIRED_08_10_25 to get UNIQUE ticker and using file instruments.csv get instrument keys and subscribe to those symbole.
1)4) Strore Result in Upstox_date.txt file with  tickers from BBSCAN_FIRED_08_10_25 file ( Instrument Keys is UPSTOX interanl )
1)5) Check this file every 2 minute and subscibe new symboles
1)6) Extract Bubblechart LOGIC to create BUBBLE chart
1
FEATURE 2)  FOR BUBBLECHART INTERNAL LOGIC UPDATE 
2) 1}LOAD Data in lowest TF available , 
2) 2}make respective changed in bubble_chart_logic.py file
2) 3}in BubbleChart.html add filter (Bubble Threshold) and (Big Player Qty) 
2) 4}use them for threshold and bigPlayerThreshold.
2) 5}Use LOWER timeframe Data for change event of Time Interval and recalculate values at local level based on loaded tick data array
2) 6} Similarly change for threshold and big player threshold . do calculations locally in JS
2) 7}This will avoid RELOAD time and unnecessory calls to api when data is available. Make necessory changes in PYTHON and HTML 

THIS Will be very useful in live feed condition , if user changes TimeFrame (TF ) then app-page dont need to reload all data one more time just for TF change, When you have tick level data you can always do TF conversion to higher TF



 
