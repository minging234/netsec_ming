#!/bin/bash
case $1 in
    "pg" )
        case $2 in
            "i" )
                pip install git+https://github.com/CrimsonVista/Playground3.git@master
                exit
            ;;

            "u" )
                pip install git+https://github.com/CrimsonVista/Playground3.git@master --upgrade
                exit
            ;;

            * ) echo "Incorrect args"
        esac
        exit
    ;;

    * ) echo "Incorrect args"

esac
