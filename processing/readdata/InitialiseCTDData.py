import os, statistics, time, logging, traceback
import sqlite3
import processing.RefreshFunction

# Reads in the .ros file from Seasave for getting bottle data...
# Not very complicated, no GUI, just pure function to take the .ros and parse it to the database file


class initCTDdata():
    def __init__(self, file, database, path, project, interactive, rereading):

        self.file = file

        self.database = database

        self.currpath = path

        self.currproject = project

        self.interactive = interactive

        self.rereading = rereading

        self.filepath = self.currpath + '/' + 'CTD' + '/' + self.file

        self.loadfilein()

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
            bottlesfired = [float(x[bottlesfiredindex[0]]) for x in self.datalist]

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
                timelapsed = [float(x[timelapsedindex[0]]) for x in self.datalist]
            else:
                scansindex = self.substringindex(self.sensorlist, 'scan')
                timelapsed = [0.04 * float(x[scansindex[0]]) for x in self.datalist]

            starttimeindex = self.substringindex(headerlist, 'NMEA UTC')
            starttimerow = headerlist[starttimeindex[0]]
            starttime = starttimerow[20:-1]

            convertedtime = time.strptime(starttime, "%b %d %Y %H:%M:%S")
            startepochtime = time.mktime(convertedtime)

            bottlescansindex = self.substringindex(headerlist, 'scans_per_bottle')
            bottlescans = headerlist[bottlescansindex[0]]

            bottlescansnum = [int(x) for x in bottlescans.split() if x.isdigit()]
            maxnumbottles = [bottlesfired[-1]]

            temp1binned = []
            temp2binned = []
            conduct1binned = []
            conduct2binned = []
            oxygen1binned = []
            oxygen2binned = []
            pressurebinned = []
            salt1binned = []
            salt2binned = []
            bottlesfiredbinned = []
            bottlepositionbinned = []
            longitudebinned = []
            latitudebinned = []
            fluorobinned = []
            timebinned = []

            for i in range(int(maxnumbottles[0])):
                stationbinned.append(station)

                variables = ['temp1', 'temp2', 'conduct1', 'conduct2', 'oxygen1', 'oxygen2', 'pressure', 'salt1',
                             'salt2', 'bottlesfired', 'bottleposition', 'time', 'longitude', 'latitude', 'fluoro']

                temp1hold = temp1[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                temp1average = statistics.median(temp1hold)
                temp1binned.append(temp1average)

                temp2hold = temp2[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                temp2average = statistics.median(temp2hold)
                temp2binned.append(temp2average)

                conduct1hold = conduct1[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                conduct1average = statistics.median(conduct1hold)
                conduct1binned.append(conduct1average)

                conduct2hold = conduct2[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                conduct2average = statistics.median(conduct2hold)
                conduct2binned.append(conduct2average)

                oxygen1hold = oxygen1[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                oxygen1average = statistics.median(oxygen1hold)
                oxygen1binned.append(oxygen1average)

                oxygen2hold = oxygen2[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                oxygen2average = statistics.median(oxygen2hold)
                oxygen2binned.append(oxygen2average)

                pressurehold = pressure[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                pressureaverage = statistics.median(pressurehold)
                pressurebinned.append(pressureaverage)

                salt1hold = salt1[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                salt1average = statistics.median(salt1hold)
                salt1binned.append(salt1average)

                salt2hold = salt2[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                salt2average = statistics.median(salt2hold)
                salt2binned.append(salt2average)

                bottlesfiredhold = bottlesfired[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                bottlesfiredaverage = statistics.median(bottlesfiredhold)
                bottlesfiredbinned.append(bottlesfiredaverage)

                bottlepositionhold = bottleposition[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                bottlepositionaverage = statistics.median(bottlepositionhold)
                bottlepositionbinned.append(bottlepositionaverage)

                longitudehold = longitude[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                longitiudeaverage = statistics.median(longitudehold)
                longitudebinned.append(longitiudeaverage)

                latitudehold = latitude[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                latitudeaverage = statistics.median(latitudehold)
                latitudebinned.append(latitudeaverage)

                fluorohold = fluoro[(i * bottlescansnum[0]): ((i + 1) * bottlescansnum[0])]
                fluoroaverage = statistics.median(fluorohold)
                fluorobinned.append(fluoroaverage)

                timehold = (timelapsed[i * bottlescansnum[0]]) + startepochtime
                timeingmt = time.localtime(timehold)
                timetoprint = time.strftime('%Y %m %d %H:%M:%S', timeingmt)
                timebinned.append(timetoprint)

            # Pack the data up together and insert into db file
            ctddata = tuple(zip(stationbinned, temp1binned, temp2binned, conduct1binned, conduct2binned,
                                oxygen1binned, oxygen2binned, pressurebinned, salt1binned, salt2binned,
                                bottlesfiredbinned, bottlepositionbinned, timebinned, longitudebinned, latitudebinned,
                                fluorobinned))

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

            if not self.rereading:
                self.refreshing = processing.RefreshFunction.refreshFunction(self.currpath, self.currproject, self.interactive)

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
