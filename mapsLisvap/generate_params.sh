#!/bin/bash

PCRASTER_PATH=/software/PCRaster/pcraster4
COL2MAP_CMD=${PCRASTER_PATH}/bin/col2map
RESAMPLE_CMD=${PCRASTER_PATH}/bin/resample
PCRCALC_CMD=${PCRASTER_PATH}/bin/pcrcalc

DEM_MAP_5KM=/nahaUsers/gomesgo/newMapFilters/5km/dem.map
DEM_MAP_1KM=/nahaUsers/gomesgo/newMapFilters/1km/dem.map

MASK_MAP=/nahaUsers/gomesgo/newMapFilters/mask.map

INPUT_FILES_PATH=/nahaUsers/gomesgo/newMapFilters/params
OUTPUT_FILES_PATH=/nahaUsers/gomesgo/newMapFilters/params

PARAMS_LIST=angstr_a,angstr_b,supit_a,supit_b,supit_c,hargrv_a,hargrv_b
PARAMS_ARRAY=( ${PARAMS_LIST//,/ } )

echo 'Start'
echo ''

for param_name in ${PARAMS_ARRAY[@]}; do

INPUT_BASE_NAME=$param_name

echo ''
echo '# #####################'
echo '# Generating map for '${INPUT_BASE_NAME}
echo '# #####################'

# ####################################################################

echo 'Generating point file:'
echo 'Reading: '${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.txt
echo 'Using clone map: '${DEM_MAP_5KM}

$COL2MAP_CMD -a --clone "${DEM_MAP_5KM}" ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.txt ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.points ;

echo 'Writing: '${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.points

echo ''
echo 'Generating map file:'
echo 'Reading: '${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.points
echo 'Using mask map: '${MASK_MAP}

# $PCRCALC_CMD '"${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map"=inversedistance("${MASK_MAP}","${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.points",2,0,5)' ;
$PCRCALC_CMD '"'${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}'.map"=inversedistance("'${MASK_MAP}'","'${INPUT_FILES_PATH}/${INPUT_BASE_NAME}'.points",2,0,5)' ;

echo 'Writing: '${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map

# ####################################################################

# $COL2MAP_CMD -a --clone "${DEM_MAP_1KM}" ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.txt ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.map.1km ; 
# $PCRCALC_CMD '"${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.map.1km"="${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.map.1km" + (0.006 * "${DEM_MAP_1KM}")' ;
# $RESAMPLE_CMD --clone "${DEM_MAP_5KM}" ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.map.1km ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.points ;
# $PCRCALC_CMD '"${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map"=inversedistance("${MASK_MAP}","${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.points",2,0,5)' ;
# $PCRCALC_CMD '"${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map"="${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map" - (0.006 * "${DEM_MAP_5KM}")' ;

# ####################################################################

# $COL2MAP_CMD -a --clone "${DEM_MAP_1KM}" ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.txt ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.map.1km ;
# $PCRCALC_CMD '"${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.map.1km"="${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.map.1km" + (0.00025 * "${DEM_MAP_1KM}")' ;
# $RESAMPLE_CMD --clone "${DEM_MAP_5KM}" ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.map.1km ${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.points ;
# $PCRCALC_CMD '"${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map"=inversedistance("${MASK_MAP}","${INPUT_FILES_PATH}/${INPUT_BASE_NAME}.points",2,0,5)' ;
# $PCRCALC_CMD '"${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map"="${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map" - (0.00025 * "${DEM_MAP_5KM}")' ;
# $PCRCALC_CMD '"${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map"=if("${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map" lt 0.0 then 0.001 else "${OUTPUT_FILES_PATH}/${INPUT_BASE_NAME}.map")' ;

done;

echo 'Done'

