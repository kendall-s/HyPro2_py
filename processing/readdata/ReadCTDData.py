import os, statistics, time, logging, traceback
import sqlite3
import bisect
from PyQt5.QtCore import pyqtSignal, QObject

# Reads in the .ros file from Seasave for getting bottle data...
# Not very complicated, no GUI, just pure function to take the .ros and parse it to the database file


class initCTDdata(QObject):

    processing_completed = pyqtSignal()

    def __init__(self, file, database, path, project, interactive, rereading):
        super().__init__()
        self.file = file

        self.database = database
        self.currpath = path
        self.currproject = project
        self.interactive = interactive

        self.rereading = rereading

        self.filepath = self.currpath + '/' + 'CTD' + '/' + self.file

    def loadfilein(self):
        # Open file
        filebuffer = open(self.filepath)
        fullfilelist = list(filebuffer)
        filebuffer.close()

        # Find where header stops and data starts - split it up into header list and data list
        endindex = self.substringindex(fullfilelist, 'END')

        headerlist = fullfilelist[0:endindex[0]]
        rawdatalist = fullfilelist[(endindex[0]) + 1:]

        # Find station number
        stationindex = self.substringindex(headerlist, 'Station')
        stationstring = headerlist[stationindex[0]]
        station = int(stationstring[-4: -1])
        stationbinned = []

        self.datalist = []
        for row in rawdatalist:
            self.datalist.append(row.split())

        # Find names aka the sensors, figure out what channel they occupy
        # Find mention of 'name', will just use first occurance as they are consecutive
        nameindexes = self.substringindex(headerlist, 'name')
        startofnames = nameindexes[0]
        endofnames = nameindexes[-1]
        self.sensorlist = headerlist[startofnames:endofnames]

        try:
            temp1index = self.substringindex(self.sensorlist, 't090C')
            temp1 = [float(x[temp1index[0]]) for x in self.datalist]

            temp2index = self.substringindex(self.sensorlist, 't190C')
            temp2 = [float(x[temp2index[0]]) for x in self.datalist]

            conduct1index = self.substringindex(self.sensorlist, 'c0S/m')
            conduct1 = [float(x[conduct1index[0]]) for x in self.datalist]

            conduct2index = self.substringindex(self.sensorlist, 'c1S/m')
            conduct2 = [float((x[conduct2index[0]])) for x in self.datalist]

            oxygen1index = self.substringindex(self.sensorlist, 'sbeox0')
            oxygen1 = [float(x[oxygen1index[0]]) for x in self.datalist]

            oxygen2index = self.substringindex(self.sensorlist, 'sbeox1')
            oxygen2 = [float(x[oxygen2index[0]]) for x in self.datalist]

            pressureindex = self.substringindex(self.sensorlist, 'prDM')
            pressure = [float(x[pressureindex[0]]) for x in self.datalist]

            salt1index = self.substringindex(self.sensorlist, 'sal00')
            salt1 = [float(x[salt1index[0]]) for x in self.datalist]

            salt2index = self.substringindex(self.sensorlist, 'sal11')
            salt2 = [float(x[salt2index[0]]) for x in self.datalist]

            bottlesfiredindex = self.substringindex(self.sensorlist, 'nbf')
            bottlesfired = [int(x[bottlesfiredindex[0]]) for x in self.datalist]

            bottlepositionindex = self.substringindex(self.sensorlist, 'bpos')
            bottleposition = [float(x[bottlepositionindex[0]]) for x in self.datalist]

            longitudeindex = self.substringindex(self.sensorlist, 'long')
            longitude = [float(x[longitudeindex[0]]) for x in self.datalist]

            latitudeindex = self.substringindex(self.sensorlist, 'lati')
            latitude = [float(x[latitudeindex[0]]) for x in self.datalist]

            fluoroindex = self.substringindex(self.sensorlist, 'Fluorescence')
            fluoro = [float(x[fluoroindex[0]]) for x in self.datalist]

            timelapsedindex = self.substringindex(self.sensorlist, 'timeS')
            if timelapsedindex:
                time_elapsed = [float(x[timelapsedindex[0]]) for x in self.datalist]
            else:
                scansindex = self.substringindex(self.sensorlist, 'scan')
                time_elapsed = [0.04 * float(x[scansindex[0]]) for x in self.datalist]

            starttimeindex = self.substringindex(headerlist, 'NMEA UTC')
            starttimerow = headerlist[starttimeindex[0]]
            starttime = starttimerow[20:-1]

            convertedtime = time.strptime(starttime, "%b %d %Y %H:%M:%S")
            startepochtime = time.mktime(convertedtime)

            bottlescansindex = self.substringindex(headerlist, 'scans_per_bottle')
            bottlescans = headerlist[bottlescansindex[0]]

            bottlescansnum = [int(x) for x in bottlescans.split() if x.isdigit()]
            max_num_bottles = int([bottlesfired[-1]][0])

            temp1_binned = []
            temp2_binned = []
            conduct1_binned = []
            conduct2_binned = []
            oxygen1_binned = []
            oxygen2_binned = []
            pressure_binned = []
            salt1_binned = []
            salt2_binned = []
            bottles_fired_binned = []
            bottle_position_binned = []
            longitude_binned = []
            latitude_binned = []
            fluoro_binned = []
            time_binned = []

            # Let's find out what rows correspond to what bottles fired
            bottle_firing_indexes = []
            for bottle_number in range(max_num_bottles):
                index = bisect.bisect_left(bottlesfired, bottle_number+1) # Bottle num+1 as range ind starts at 0
                bottle_firing_indexes.append(index)
            bottle_firing_indexes.append(len(bottlesfired))

            for i in range(max_num_bottles):
                stationbinned.append(station)

                variables = ['temp1', 'temp2', 'conduct1', 'conduct2', 'oxygen1', 'oxygen2', 'pressure', 'salt1',
                             'salt2', 'bottlesfired', 'bottleposition', 'time', 'longitude', 'latitude', 'fluoro']

                temp1_temporary = temp1[(bottle_firing_indexes[i]): bottle_firing_indexes[i+1]]
                temp1_median = statistics.median(temp1_temporary)
                temp1_binned.append(temp1_median)

                temp2_temporary = temp2[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                temp2_median = statistics.median(temp2_temporary)
                temp2_binned.append(temp1_median)

                conduct1_temporary = conduct1[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                conduct1_median = statistics.median(conduct1_temporary)
                conduct1_binned.append(conduct1_median)

                conduct2_temporary = conduct2[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                conduct2_median = statistics.median(conduct2_temporary)
                conduct2_binned.append(conduct2_median)

                oxygen1_temporary = oxygen1[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                oxygen1_median = statistics.median(oxygen1_temporary)
                oxygen1_binned.append(oxygen1_median)

                oxygen2_temporary = oxygen2[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                oxygen2_median = statistics.median(oxygen2_temporary)
                oxygen2_binned.append(oxygen2_median)

                pressure_temporary = pressure[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                pressure_median = statistics.median(pressure_temporary)
                pressure_binned.append(pressure_median)

                salt1_temporary = salt1[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                salt1_median = statistics.median(salt1_temporary)
                salt1_binned.append(salt1_median)

                salt2_temporary = salt2[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                salt2_median = statistics.median(salt2_temporary)
                salt2_binned.append(salt2_median)

                bottles_fired_temporary = bottlesfired[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                bottles_fired_median = statistics.median(bottles_fired_temporary)
                bottles_fired_binned.append(bottles_fired_median)

                bottle_position_temporary = bottleposition[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                bottle_position_median = statistics.median(bottle_position_temporary)
                bottle_position_binned.append(bottle_position_median)

                longitude_temporary = longitude[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                longitude_median = statistics.median(longitude_temporary)
                longitude_binned.append(longitude_median)

                latitude_temporary = latitude[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                latitude_median = statistics.median(latitude_temporary)
                latitude_binned.append(latitude_median)

                fluoro_temporary = fluoro[(bottle_firing_indexes[i]): bottle_firing_indexes[i + 1]]
                fluoro_median = statistics.median(fluoro_temporary)
                fluoro_binned.append(fluoro_median)

                time_temporary = time_elapsed[i] + startepochtime
                time_in_gmt = time.localtime(time_temporary)
                time_to_print = time.strftime('%Y %m %d %H:%M:%S', time_in_gmt)
                time_binned.append(time_to_print)

            # Pack the data up together and insert into db file
            ctddata = tuple(zip(stationbinned, temp1_binned, temp2_binned, conduct1_binned, conduct2_binned,
                                oxygen1_binned, oxygen2_binned, pressure_binned, salt1_binned, salt2_binned,
                                bottles_fired_binned, bottle_position_binned, time_binned, longitude_binned,
                                latitude_binned,fluoro_binned))

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.executemany('INSERT OR IGNORE INTO ctdData VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', ctddata)
            conn.commit()
            conn.close()

            # Make sure to add it to the processed file list...
            modtime = float(os.path.getmtime(self.filepath))
            holder = ((self.file, modtime),)

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.executemany('INSERT OR REPLACE INTO ctdFilesProcessed VALUES(?,?)', holder)
            conn.commit()

            logging.info('CTD file ' + str(self.file) + ' processed')

            #if not self.rereading:
            self.processing_completed.emit()

        except Exception:
            logging.error(traceback.print_exc())
            print(traceback.print_exc())

    def substringindex(self, list, substring):
        temp = []
        for i, s in enumerate(list):
            if substring in s:
                temp.append(i)
        if temp:
            return temp
        else:
            return False
