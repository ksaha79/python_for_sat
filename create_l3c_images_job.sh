#!/bin/bash
#
: ${THISDIR:=$(dirname $(readlink --canonicalize --no-newline ${BASH_SOURCE[0]}))}

 Max_Num_CPUs=$(grep -c ^processor /proc/cpuinfo)
 declare -r -a cpu_avail_default=(`seq 0 $((Max_Num_CPUs-1))`)
 if [ -z ${cpu_avail+x} ]; then
    declare -a cpu_avail=("${cpu_avail_default[@]}")
 fi
 declare -a cpu_status

 echoerr() {
   echo "$@" 1>&2
 }

 year_end() {
   date -d "$1-12-31" +%j
 }

 init_cpu_status() {
   local i
   for i in $(seq 0 $((${#cpu_avail[@]}-1))); do
      (( cpu_status[$i] = 0 ))
   done
   echoerr "$(date +'%F %T') miniTask CPU manager: **** Initial CPUs. All (${#cpu_avail[@]}) CPUs are availbale. ****"
 }

 wait_all_jobs() {
   wait
   echoerr "$(date +'%F %T') miniTask CPU manager: **** Taskset jobs end. All (${#cpu_avail[@]}) CPUs are availbale. ****"
 }

 update_cpu_status() {
   local i
   for i in $(seq 0 $((${#cpu_avail[@]}-1))); do
      if (( ${cpu_status[$i]} > 0 )); then
        if [ -z "$(ps --no-heading -p ${cpu_status[$i]})" ]; then
          echoerr "$(date +'%F %T') miniTask CPU manager: Process ${cpu_status[$i]} is completed."
          echoerr "$(date +'%F %T') miniTask CPU manager: Status of CPU $i is set to idle."
          (( cpu_status[$i] = 0 ))
        fi
      fi
   done
 }

 set_cpu_busy() {
   (( cpu_status[$1] = $2 ))
   echoerr "$(date +'%F %T') miniTask CPU manager: CPU $1 was idle. Now process pid=$2 is running on it."
 }

 get_free_cpu() {
   local i
   update_cpu_status
   for i in $(seq 0 $((${#cpu_avail[@]}-1))); do
      if (( cpu_status[$i] == 0 )); then
         echoerr "$(date +'%F %T') miniTask CPU manager: CPU $i is availbale for running new process."
         eval $2=$i
         return
      fi
   done
   (( $1 < 2 )) && echoerr "$(date +'%F %T') miniTask CPU manager: All (${#cpu_avail[@]}) CPUs are busy now. Check late."
   (( $1 == 2 )) && echoerr "$(date +'%F %T') miniTask CPU manager: Skip duplicate lines ... ..."
   eval $2=-1
 }

 free_cpu_id() {
    local -i c=0
    local id
    get_free_cpu $c id
    while (( id == -1 )); do
      sleep 10s
      get_free_cpu $c id
      c=c+1
    done
    eval $1=$id
 }

 physical_cpu() {
    eval $2=${cpu_avail[$1]}  # $1: logical CPU id - return from free_cpu_id()
 }

####################################################################################

#set -x

 cd $THISDIR

 declare -i year startj endj j jj

 (( $# == 0 || $# > 3 )) && {
   echoerr "usage: $(basename $0) year [startjday [endjday]]"
   exit
 }
 year=$1; startj=1; endj=$(year_end ${year})
 (( $# > 1 )) && {
   (( $2 > endj )) && {
     echoerr "usage: $(basename $0) year [startjday [endjday]]"
     echoerr "      ?! startjday exceeds the last day of the year"
     exit
   }
   startj=$2
   (( $# > 2 )) && {
     (( $3 < startj )) && {
       echoerr "usage: $(basename $0) year [startjday [endjday]]"
       echoerr "      ?! endjday is less than startjday"
       exit
     }
     (( $3 > endj )) && {
       echoerr "usage: $(basename $0) year [startjday [endjday]]"
       echoerr "      ?! endjday exceeds the last day of the year"
       exit
     }
     endj=$3
   }
 }

 declare cid pcid
# cpu_avail=(`seq 0 $((Max_Num_CPUs-1))`)
 cpu_avail=(3 4 5 6 7)
 init_cpu_status

#Dat_Dir=/srv/work_002/Data_PFV53/PFV53_NC_L3C
#Dat_Dir=/srv/pfv53_l3c
# Dat_Dir=/nodc/projects/satdata.5/Converters/Data_PFV53/PFV53_NC_L3C
 Dat_Dir=/nodc/projects/satdata.4/pfv53-aws/SIP
 Out_Dir=$THISDIR/L3C_IMAGES
 Log_Dir=$THISDIR/LOG

 ddir=$Dat_Dir/$year
 odir=$Out_Dir/$year
 ldir=$Log_Dir/$year
 [ -d $odir ] || mkdir -p $odir
 [ -d $ldir ] || mkdir -p $ldir

 for (( j = startj; j <= endj; j++ )); do
    jj=year*1000+j
    for infile in $ddir/*_G_${jj}_*.nc; do
#       for varName in quality_level pathfinder_quality_level l2p_flag \
#                      sea_surface_temperature declouded_sst dt_analysis \
#                      aerosol_dynamic_indicator sea_ice_fraction wind_speed; do
       for varName in sea_surface_temperature; do
          outfile=$odir/$(basename $infile .nc)_$varName.png
          free_cpu_id cid
          physical_cpu $cid pcid
          echo taskset -c $pcid $THISDIR/image_pfv5.3_l3c_$varName.py -i $infile -o $outfile
          taskset -c $pcid $THISDIR/image_pfv5.3_l3c_$varName.py -i $infile -o $outfile \
                    >& $ldir/image_pfv5.3_l3c_${varName}_J${jj}_$cid.log &
          pid=$!
          set_cpu_busy $cid $pid
       done
    done
 done

 wait_all_jobs     # wait for all previous taskset processes to complete

# ------ end of scripts ------

