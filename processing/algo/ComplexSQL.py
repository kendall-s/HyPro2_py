"""

Yeah, yeah, yeah, I know. This is ugly and most likely a product of my piss poor database design, but with close
to 10k samples to join together, these queries make sure it happens in a fraction of a second. Which is good enough
for me.

"""


export_ctd_data = \
f"""
select 
logsheetData.deployment, 
logsheetData.rosettePosition,
ctdData.pressure,
ctdData.temp1,
ctdData.temp2,
ctdData.salt1,
ctdData.salt2,
ctdData.oxygen1,
ctdData.oxygen2,
ctdData.fluoro,
ctdData.time,
ctdData.longitude,
ctdData.latitude,
logsheetData.nutrient, 
ammonia.concentration as amm_conc,
ammonia.flag, 
nitrate.concentration as nitrate_conc, 
nitrate.flag,
nitrite.concentration as nitrite_conc,
nitrite.flag,
phosphate.concentration as phos_conc, 
phosphate.flag,
silicate.concentration as sil_conc, 
silicate.flag,
salinityData.salinity,
salinityData.flag,
oxygenData.oxygen,
oxygenData.oxygenMoles,
oxygenData.flag

from logsheetData 

left join 
(select 
avg(ammoniaData.concentration) as concentration, 
ammoniaData.sampleID,
ammoniaData.deployment,
ammoniaData.rosettePosition,
ammoniaData.time,
ammoniaData.flag
from ammoniaData
where ammoniaData.flag in (1)
group by ammoniaData.sampleID
having count(ammoniaData.sampleID) > 1

union

select 
ammoniaData.concentration,
ammoniaData.sampleID,
ammoniaData.deployment,
ammoniaData.rosettePosition,
ammoniaData.time,
ammoniaData.flag
from ammoniaData
where ammoniaData.flag in (1)
group by ammoniaData.sampleID
having count(ammoniaData.sampleID) = 1) 
as ammonia 
on (ammonia.deployment = logsheetData.deployment and  ammonia.rosettePosition = logsheetData.rosettePosition)

left join 
(select 
avg(nitrateData.concentration) as concentration, 
nitrateData.sampleID,
nitrateData.deployment,
nitrateData.rosettePosition,
nitrateData.time,
nitrateData.flag
from nitrateData
where nitrateData.flag in (1)
group by nitrateData.sampleID
having count(nitrateData.sampleID) > 1

union

select 
nitrateData.concentration,
nitrateData.sampleID,
nitrateData.deployment,
nitrateData.rosettePosition,
nitrateData.time,
nitrateData.flag
from nitrateData
where nitrateData.flag in (1)
group by nitrateData.sampleID
having count(nitrateData.sampleID) = 1) 
as nitrate 
on (nitrate.deployment = logsheetData.deployment and  nitrate.rosettePosition = logsheetData.rosettePosition)

left join 
(select 
avg(nitriteData.concentration) as concentration, 
nitriteData.sampleID,
nitriteData.deployment,
nitriteData.rosettePosition,
nitriteData.time,
nitriteData.flag
from nitriteData
where nitriteData.flag in (1)
group by nitriteData.sampleID
having count(nitriteData.sampleID) > 1

union

select 
nitriteData.concentration,
nitriteData.sampleID,
nitriteData.deployment,
nitriteData.rosettePosition,
nitriteData.time,
nitriteData.flag
from nitriteData
where nitriteData.flag in (1)
group by nitriteData.sampleID
having count(nitriteData.sampleID) = 1) 
as nitrite 
on (nitrite.deployment = logsheetData.deployment and  nitrite.rosettePosition = logsheetData.rosettePosition)

left join 
(select 
avg(phosphateData.concentration) as concentration, 
phosphateData.sampleID,
phosphateData.deployment,
phosphateData.rosettePosition,
phosphateData.time,
phosphateData.flag
from phosphateData
where phosphateData.flag in (1)
group by phosphateData.sampleID
having count(phosphateData.sampleID) > 1

union

select 
phosphateData.concentration,
phosphateData.sampleID,
phosphateData.deployment,
phosphateData.rosettePosition,
phosphateData.time,
phosphateData.flag
from phosphateData
where phosphateData.flag in (1)
group by phosphateData.sampleID
having count(phosphateData.sampleID) = 1) 
as phosphate 
on (phosphate.deployment = logsheetData.deployment and  phosphate.rosettePosition = logsheetData.rosettePosition)

left join 
(select 
avg(silicateData.concentration) as concentration, 
silicateData.sampleID,
silicateData.deployment,
silicateData.rosettePosition,
silicateData.time,
silicateData.flag
from silicateData
where silicateData.flag in (1)
group by silicateData.sampleID
having count(silicateData.sampleID) > 1
union
select 
silicateData.concentration,
silicateData.sampleID,
silicateData.deployment,
silicateData.rosettePosition,
silicateData.time,
silicateData.flag
from silicateData
where silicateData.flag in (1)
group by silicateData.sampleID
having count(silicateData.sampleID) = 1) 
as silicate 
on (silicate.deployment = logsheetData.deployment and  silicate.rosettePosition = logsheetData.rosettePosition)

left join salinityData on (salinityData.deployment = logsheetData.deployment and salinityData.rosettePosition = logsheetData.rosettePosition)
left join oxygenData on (oxygenData.deployment = logsheetData.deployment and oxygenData.rosettePosition = logsheetData.rosettePosition)
left join ctdData on ctdData.deployment = (logsheetData.deployment and ctdData.rosettePosition = logsheetData.rosettePosition)

where logsheetData.nutrient != "" and logsheetData.deployment in (%s)
"""


# This query and the one after it are identical - except for a WHERE filter for the survey!
# export_all_nuts does not include survey so it just grabs everything

export_all_nuts = \
"""
select
nutrientMeasurements.runNumber,
nutrientMeasurements.sampleID,
nutrientMeasurements.cupType,
nutrientMeasurements.peakNumber,
nutrientMeasurements.survey,
nutrientMeasurements.deployment,
nutrientMeasurements.rosettePosition,
ammoniaData.concentration as amm_conc,
ammoniaData.flag, 
nitrateData.concentration as nitrate_conc, 
nitrateData.flag,
nitriteData.concentration as nitrite_conc,
nitriteData.flag,
phosphateData.concentration as phos_conc, 
phosphateData.flag,
silicateData.concentration as sil_conc, 
silicateData.flag

from nutrientMeasurements

left join
ammoniaData
on ammoniaData.time = nutrientMeasurements.time

left join 
nitrateData
on nitrateData.time = nutrientMeasurements.time

left join 
nitriteData
on nitriteData.time = nutrientMeasurements.time

left join 
phosphateData
on phosphateData.time = nutrientMeasurements.time

left join 
silicateData
on silicateData.time = nutrientMeasurements.time

where nutrientMeasurements.%s in (%s)
"""


export_all_nuts_in_survey = \
"""
select
nutrientMeasurements.runNumber,
nutrientMeasurements.sampleID,
nutrientMeasurements.cupType,
nutrientMeasurements.peakNumber,
nutrientMeasurements.survey,
nutrientMeasurements.deployment,
nutrientMeasurements.rosettePosition,
ammoniaData.concentration as amm_conc,
ammoniaData.flag, 
nitrateData.concentration as nitrate_conc, 
nitrateData.flag,
nitriteData.concentration as nitrite_conc,
nitriteData.flag,
phosphateData.concentration as phos_conc, 
phosphateData.flag,
silicateData.concentration as sil_conc, 
silicateData.flag

from nutrientMeasurements

left join
ammoniaData
on ammoniaData.time = nutrientMeasurements.time

left join 
nitrateData
on nitrateData.time = nutrientMeasurements.time

left join 
nitriteData
on nitriteData.time = nutrientMeasurements.time

left join 
phosphateData
on phosphateData.time = nutrientMeasurements.time

left join 
silicateData
on silicateData.time = nutrientMeasurements.time

where nutrientMeasurements.%s in (%s) and nutrientMeasurements.survey = ?
"""