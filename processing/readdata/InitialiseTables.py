import sqlite3
from sqlite3 import Error
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, select

from processing.data.Models import *

# This is a dirty file left over from the start, all it essentially is used for is completing the setup of
# the database and the tables within, it is kept as it is needed for new projects...
# TODO: rewrite to clean up..?

# Function to start connection to database file
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as ee:
        print(ee)

    return None


# Function to make sure tables are created...
def form_tables(database):
    conn = create_connection(database)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS phosphateData 
                        (runNumber INTEGER,
                        cupType TEXT,
                        sampleID TEXT,
                        peakNumber INTEGER,
                        rawAD FLOAT,
                        correctedAD FLOAT,
                        concentration FLOAT, 
                        survey TEXT,
                        deployment INTEGER,
                        rosettePosition INTEGER,
                        flag INTEGER, 
                        dilution FLOAT,
                        time FLOAT,
                        UNIQUE(runNumber, peakNumber))''')

    c.execute('''CREATE TABLE IF NOT EXISTS nitrateData 
                        (runNumber INTEGER,
                        cupType TEXT,
                        sampleID TEXT,
                        peakNumber INTEGER,
                        rawAD FLOAT,
                        correctedAD FLOAT,
                        concentration FLOAT, 
                        survey TEXT,
                        deployment INTEGER,
                        rosettePosition INTEGER,
                        flag INTEGER, 
                        dilution FLOAT,
                        time FLOAT,
                        UNIQUE(runNumber, peakNumber))''')

    c.execute('''CREATE TABLE IF NOT EXISTS nitriteData 
                        (runNumber INTEGER,
                        cupType TEXT,
                        sampleID TEXT,
                        peakNumber INTEGER,
                        rawAD FLOAT,
                        correctedAD FLOAT,
                        concentration FLOAT, 
                        survey TEXT,
                        deployment INTEGER, 
                        rosettePosition INTEGER,
                        flag INTEGER,
                        dilution FLOAT,
                        time FLOAT,
                        UNIQUE(runNumber, peakNumber))''')

    c.execute('''CREATE TABLE IF NOT EXISTS ammoniaData 
                        (runNumber INTEGER,
                        cupType TEXT,
                        sampleID TEXT,
                        peakNumber INTEGER,
                        rawAD FLOAT,
                        correctedAD FLOAT,
                        concentration FLOAT, 
                        survey TEXT,
                        deployment INTEGER,
                        rosettePosition INTEGER,
                        flag INTEGER,
                        dilution FLOAT, 
                        time FLOAT,
                        UNIQUE(runNumber, peakNumber))''')

    c.execute('''CREATE TABLE IF NOT EXISTS silicateData 
                        (runNumber INTEGER,
                        cupType TEXT,
                        sampleID TEXT,
                        peakNumber INTEGER,
                        rawAD FLOAT,
                        correctedAD FLOAT,
                        concentration FLOAT, 
                        survey TEXT,
                        deployment INTEGER,
                        rosettePosition INTEGER, 
                        flag INTEGER,
                        dilution FLOAT,
                        time FLOAT,
                        UNIQUE(runNumber, peakNumber))''')


    c.execute('''CREATE TABLE IF NOT EXISTS salinityData
                        (runNumber INTEGER,
                        sampleid TEXT,
                        bottleLabel TEXT,
                        dateTime FLOAT,
                        bathTemp FLOAT,
                        uncorrectedRatio FLOAT,
                        uncorrectedRatioStdev FLOAT,
                        salinity FLOAT,
                        salinityStdev FLOAT,
                        comment TEXT,
                        flag INTEGER,
                        deployment INTEGER,
                        rosettePosition INTEGER,
                        survey TEXT,
                        UNIQUE(runNumber, dateTime))''')

    c.execute('''CREATE TABLE IF NOT EXISTS oxygenData
                        (runNumber INTEGER,
                        stationNumber INTEGER,
                        castNumber INTEGER,
                        rosette INTEGER,
                        bottleID INTEGER,
                        flaskVolume FLOAT,
                        rawTiter FLOAT,
                        titer FLOAT,
                        oxygen FLOAT,
                        oxygenMoles FLOAT,
                        thioTemp FLOAT,
                        drawTemp FLOAT,
                        finalVolts FLOAT,
                        time FLOAT,
                        flag INTEGER,
                        deployment INTEGER,
                        rosettePosition INTEGER,
                        survey TEXT,
                        UNIQUE(runNumber, time))''')

    c.execute('''CREATE TABLE IF NOT EXISTS oxygenHeader
                        (runNumber INTEGER,
                        iodateNorm FLOAT,
                        iodateTemp FLOAT,
                        iodateVol FLOAT,
                        thioNorm FLOAT,
                        thioTemp FLOAT,
                        averageTiter FLOAT,
                        blank FLOAT,
                        UNIQUE(runNumber))''')

    c.execute('''CREATE TABLE IF NOT EXISTS ctdOxygenCalibrationData
                        (deployment INTEGER,
                        rosettePosition INTEGER,
                        oxygenMoles FLOAT,
                        oxygenFlag INTEGER,
                        oxygenProcTime FLOAT,
                        UNIQUE(deployment, rosettePosition))''')

    c.execute('''CREATE TABLE IF NOT EXISTS ctdSalinityCalibrationData
                        (deployment INTEGER,
                        rosettePosition INTEGER,
                        salinityPsu FLOAT,
                        salinityTemp FLOAT,
                        salinityFlag INTEGER,
                        salinityProcTime FLOAT, 
                        UNIQUE(deployment, rosettePosition))''')

    c.execute('''CREATE TABLE IF NOT EXISTS nutrientFilesProcessed
                        (filename TEXT, 
                        timelastmodified FLOAT, UNIQUE(filename))''')

    c.execute('''CREATE TABLE IF NOT EXISTS oxygenFilesProcessed
                        (filename TEXT, 
                        timelastmodified FLOAT, UNIQUE(filename))''')

    c.execute('''CREATE TABLE IF NOT EXISTS salinityFilesProcessed
                        (filename TEXT, 
                        timelastmodified FLOAT, UNIQUE(filename))''')

    c.execute('''CREATE TABLE IF NOT EXISTS ctdFilesProcessed
                        (filename TEXT, 
                        timelastmodified FLOAT, UNIQUE(filename))''')

    c.execute('''CREATE TABLE IF NOT EXISTS logsheetFilesProcessed
                        (filename TEXT, 
                        timelastmodified FLOAT, UNIQUE(filename))''')

    c.execute('''CREATE TABLE IF NOT EXISTS ctdData
                        (deployment INTEGER, 
                        temp1 FLOAT,
                        temp2 FLOAT,
                        conduct1 FLOAT,
                        conduct2 FLOAT,
                        oxygen1 FLOAT,
                        oxygen2 FLOAT,
                        pressure FLOAT,
                        salt1 FLOAT,
                        salt2 FLOAT,
                        bottlesfired INTEGER,
                        rosettePosition INTEGER,
                        time FLOAT,
                        longitude FLOAT,
                        latitude FLOAT,
                        fluoro FLOAT, UNIQUE(deployment, rosettePosition))''')

    c.execute('''CREATE TABLE IF NOT EXISTS logsheetData
                        (deployment INTEGER, 
                        rosettePosition INTEGER,
                        oxygen INTEGER,
                        oxygenTemp FLOAT,
                        salinity TEXT,
                        nutrient INTEGER, UNIQUE(deployment, rosettePosition))''')

    c.execute('''CREATE TABLE IF NOT EXISTS underwayNutrients
                        (latitude FLOAT,
                        longitude FLOAT,
                        time FLOAT,
                        nitrate FLOAT,
                        phosphate FLOAT,
                        silicate FLOAT, 
                        nitrite FLOAT,
                        ammonia FLOAT,
                        file INTEGER, UNIQUE(time))''')

    c.execute('''CREATE TABLE IF NOT EXISTS nutrientHeader
                         (nutrient TEXT,
                         runNumber INTEGER,
                         channel INTEGER,
                         gain INTEGER,
                         baseOffset INTEGER,
                         carryoverCoef FLOAT,
                         calZeroMean FLOAT,
                         calCoef1 FLOAT,
                         calCoef2 FLOAT, UNIQUE(nutrient, runNumber))''')

    c.execute(''' CREATE TABLE IF NOT EXISTS nutrientCalibrants
                        (nutrient TEXT,
                        runNumber INTEGER,
                        calibrantIndexes INTEGER,
                        calibrantMedians FLOAT,
                        calibrantMediansZero FLOAT,
                        calibrantConcs FLOAT,
                        calibrantWeights FLOAT,
                        calibrantResiduals FLOAT,
                        calibrantFlags INTEGER, UNIQUE(nutrient, runNumber, calibrantIndexes))''')

    c.execute(''' CREATE TABLE IF NOT EXISTS nutrientBaselines
                        (nutrient TEXT, 
                        runNumber INTEGER,
                        baselineIndexes INTEGER,
                        baselinePeakStarts INTEGER,
                        baselineMedians FLOAT,
                        baselineFlags INTEGER, UNIQUE(nutrient, runNumber, baselineIndexes))''')

    c.execute(''' CREATE TABLE IF NOT EXISTS nutrientDrifts
                        (nutrient TEXT,
                        runNumber INTEGER,
                        driftIndexes INTEGER,
                        driftPeakStarts INTEGER,
                        driftMedians FLOAT,
                        driftFlags INTEGER, UNIQUE(nutrient, runNumber, driftIndexes))''')

    c.execute(''' CREATE TABLE IF NOT EXISTS nutrientMeasurements
                        (runNumber INTEGER,
                        sampleID TEXT,
                        cupType TEXT,
                        peakNumber INTEGER,
                        survey TEXT,
                        deployment TEXT,
                        rosettePosition TEXT,
                        time FLOAT,
                        UNIQUE(time))''')

    conn.commit()
    conn.close()

    engine = create_engine(f"sqlite+pysqlite:///C:/HyPro/sqlite_sqlalchemy_testing_db.db", echo=False)
    Base.metadata.create_all(engine, checkfirst=True)
    engine.dispose()

    print('Data tables created and running')

# Main function for script
def main(project, path):
    projectinuse = project
    databasefile = path + "/" + projectinuse + "Data.db"
    form_tables(databasefile)
