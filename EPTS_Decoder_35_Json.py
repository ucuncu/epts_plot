# Implement and Analysis Data for EPTS Device SD Card Log Data
import json
import re
import codecs
from gmplot import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import itertools
import math
from numpy import diff
import scipy.integrate
import csv
import simplekml


DataJSON = True

plt.style.use('seaborn-pastel')

#constants
dateTrain = '240620'
timeStart = 194700
timeEnd = 200000
#BBox = [33.93716, 33.94605, 36.37322, 36.37735] # map mahalle
BBox = [33.93958, 33.94327, 36.37437, 36.37651] # map mahalle kucuk
ruh_m = plt.imread('map_mahalle_kucuk.png')

#variables
lat = []
lon = []
accVal = []
accValX = []
accValY = []
accValZ = []
magValX = []
magValY = []
magValZ = []
gyroValX = []
gyroValY = []
gyroValZ = []
gpsAlt = []
gpsVel = []
timeSeries = []
errorCnt = 0
jsonErrorCnt = 0
x_remove_cs = ''
errorCnt = 0
validDataCnt = 0

#functions
def measureDistance(lat1, lon1, lat2, lon2): #mearure the distance between two coordinates
    R = 6378.137; # Radius of earth in KM
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180;
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180;
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(dLon/2) * math.sin(dLon/2);
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
    d = R * c;
    return d * 1000; #meters



# Read and decode the log data    
f = open("Testler/eptsdat4-atikmah.TXT", 'r', encoding="utf-8", errors='ignore');
print('File Openned')
file_content = f.readlines()
f.close()
print('File Closed')
line_qty = len(file_content)
cntUnvalidData = 0;
cntUnvalidJSON = 0;
cntFilteredData = 0;
content = [x.strip() for x in file_content]


for file_lines in content:
    try:
        x = file_lines
        cntStart = 0
        cntEnd = 0
        fDataValid = False
        lineEndChars = re.search('}}$', x)
        lineStartChars =re.search(r'{\"GPS\":', x )
        endOfFile = re.search('&', x)
        if lineEndChars and lineStartChars and not endOfFile:
            pass
        else:
            content.remove(x)
            cntUnvalidData = cntUnvalidData + 1
    except ValueError:
         errorCnt = errorCnt + 1;
    
for all_content in content:
    try:
        json_content = json.loads(all_content)
        if 'Lat' and 'Lon' in json_content['GPS']:  #buraya oluşabilecek tüm hataları yazmak lazım, try expect çalışmadı düzgün....
            if int(json_content['GPS']['Fix']) > 0 and json_content['GPS']['Date'] == dateTrain:
                if float(json_content['GPS']['Lat']) > 0 and float(json_content['GPS']['Lon']) > 0:
                    if float(json_content['GPS']['Time']) > timeStart and float(json_content['GPS']['Time']) < timeEnd:
                        lat.append(float(json_content['GPS']['Lat']))
                        lon.append(float(json_content['GPS']['Lon']))
                        timeSeries.append(float(json_content['GPS']['Time']))
                        accValX.append(9.8*json_content['Acc']['X']/1000)
                        accValY.append(9.8*json_content['Acc']['Y']/1000)
                        accValZ.append(9.8*json_content['Acc']['Z']/1000)
                        magValX.append(json_content['Mag']['X'])
                        magValY.append(json_content['Mag']['Y'])
                        magValZ.append(json_content['Mag']['Z'])
                        gyroValX.append(json_content['Gyro']['X']/1000)
                        gyroValY.append(json_content['Gyro']['Y']/1000)
                        gyroValZ.append(json_content['Gyro']['Z']/1000)
                        gpsAlt.append(float(json_content['GPS']['Alt']))
                        gpsVel.append(3.6*0.514*float(json_content['GPS']['Vel']))
    except ValueError:
         jsonErrorCnt = jsonErrorCnt + 1;  
print('Json Error Rate = %', 100*(jsonErrorCnt /len(content)))


fig = plt.figure(1)
ax1 = fig.add_subplot(311)
ax1.set_ylabel('Accel.(m/s^2)')
ax1.set_title('Accelerometer graph on X,Y,Z axis')
t = np.asarray(timeSeries)
accX = np.asarray(accValX)
accY = np.asarray(accValY)
accZ = np.asarray(accValZ) 
line, = ax1.plot(t,accX, color='blue', label='accX', lw=2)
line, = ax1.plot(t,accY, color='red', label='accY', lw=2)
line, = ax1.plot(t,accZ, color='green', label='accZ', lw=2)
ax1.legend()

ax2 = fig.add_subplot(312)
ax2.set_ylabel('Angular Vel.(dps)')
ax2.set_title('Gyroscope graph on X,Y,Z axis')
t = np.asarray(timeSeries)
gyroX = np.asarray(gyroValX)
gyroY = np.asarray(gyroValY)
gyroZ = np.asarray(gyroValZ) 
line, = ax2.plot(t,gyroX, color='blue', label='gyroX', lw=2)
line, = ax2.plot(t,gyroY, color='red', label='gyroY',  lw=2)
line, = ax2.plot(t,gyroZ, color='green', label='gyroZ',  lw=2)
ax2.legend()

ax3 = fig.add_subplot(313)
ax3.set_ylabel('uT')
ax3.set_title('Magnetometer graph on X,Y,Z axis')
t = np.asarray(timeSeries)
magX = np.asarray(magValX)
magY = np.asarray(magValY)
magZ = np.asarray(magValZ) 
line, = ax3.plot(t,magX, color='blue', label='magX',  lw=2)
line, = ax3.plot(t,magY, color='red', label='magY', lw=2)
line, = ax3.plot(t,magZ, color='green', label='magZ', lw=2)
ax3.legend()


#store lat and lon in a more readible form       
latitude_list = lat
longitude_list = lon
data_coor = []
for lat_list, lon_list in itertools.product(latitude_list, longitude_list):
    data_list_tmp = (lat_list, lon_list)
    data_coor.append(data_list_tmp)
measurements = measurements = np.asarray(data_coor)


diffBetweenMeasurements = [measureDistance(latitude_list[i+1],longitude_list[i+1],latitude_list[i],longitude_list[i]) for i in range(len(longitude_list)-1)]
for i in range(len(longitude_list)-1):
    if diffBetweenMeasurements[i] > 3:        
        print(diffBetweenMeasurements[i])
print('Total Sum of the differences between 2 measurements: ',sum(diffBetweenMeasurements))
print('Variance of measurements: ',np.var(diffBetweenMeasurements))
print('Max difference between 2 measurements: ',max(diffBetweenMeasurements))


x = []
y = []
def init():
    line.set_data([], [])
    return line,
def animate(i):
    y.append(latitude_list[i])
    x.append(longitude_list[i])
    line.set_data(x, y)
    return line,

fig2, ax = plt.subplots(figsize = (8,8))
#ax.scatter([], [], zorder=1, alpha= 0.2, c='b', s=10)
ax.set_title('Living Test for EPTS Device')
ax.set_xlim(BBox[0],BBox[1])
ax.set_ylim(BBox[2],BBox[3])
ax.get_xaxis().get_major_formatter().set_useOffset(False)
ax.get_xaxis().get_major_formatter().set_scientific(False)
ax.get_yaxis().get_major_formatter().set_useOffset(False)
ax.get_yaxis().get_major_formatter().set_scientific(False)
ax.imshow(ruh_m, zorder=0, extent = BBox, aspect= 'equal')
line, = ax.plot([], [], color='#fb9214', lw=4)

anim = FuncAnimation(fig, animate, init_func=init, frames=len(latitude_list)-1, interval=0.01, blit=True)

# Draw the GPS line On Google Maps on a HTML page.
gmap = gmplot.GoogleMapPlotter(latitude_list[0], longitude_list[0], 20)
gmap.plot(latitude_list,longitude_list,edge_width=4,color='cornflowerblue')
gmap.scatter(latitude_list,longitude_list,'#fb9214', size = 0.4, marker = False)
gmap.marker(latitude_list[0], longitude_list[0], color = 'red', title = 'start point')
gmap.coloricon
gmap.apikey = "AIzaSyCLfWwWJhjH4hbph9N6X3GTgWr4bboLUQ0"
gmap.draw( "map.html")




# Show Figures
print('---SHOW FIGURES---')
#fig.tight_layout(pad=1.0)
plt.show()

