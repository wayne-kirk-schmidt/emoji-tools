Emoji Tools
===========

Emoji Tools are designed to help convert code points in emojis into something you can display.

It builds on research Mat Gritt has on working out the conversion methods from code points to Unicode.
Using the methods, any large sequence of emoji code points can be converted

The reference for the Emojis currently is:

https://unicode.org/emoji/charts

Installing the Scripts
=======================

The scripts are designed to be used within a batch script or DevOPs tool such as Chef or Ansible.
Each script is written in python3, and a list of python modules is provided to aid people using a pip install.

You will need to use Python 3.6 or higher and the modules listed in the dependency section.  

The steps are as follows: 

    1. Download and install python 3.6 or higher from python.org. Append python3 to the LIB and PATH env.

    2. Download and install git for your platform if you don't already have it installed.
       It can be downloaded from https://git-scm.com/downloads
    
    3. Open a new shell/command prompt. It must be new since only a new shell will include the new python 
       path that was created in step 1. Change to the folder where you want to install the scripts.
    
    4. Execute the following command to install pipenv, which will manage all of the library dependencies:
    
        sudo -H pip3 install pipenv 
 
    5. Clone this repository. This will create a new folder
    
    6. Change into this folder. Type the following to install all the package dependencies 
       (this may take a while as this will download all of the libraries it uses):

        pipenv install
        
Dependencies
============

See the contents of "pipfile"

Script Names and Purposes
=========================

The scripts are organized into sub directories:

    1. ./bin - has all of the scripts here

            ./bin/emoji_download.py - downloads the emoji file
            ./bin/emoji_translate.py - translates a given emoji code point
            ./bin/emoji_process.py - downloads and translates the emoji file

    2. ./doc - this has refernce information including sample emojis 

Examples
========

            ./bin/emoji_process.py https://unicode.org/emoji/charts/full-emoji-list.html | egrep -i wales   
# REFERENCE # flag_wales # U+1F3F4 U+E0067 U+E0062 U+E0077 U+E006C U+E0073 U+E007F
# CONVERTED # flag_wales # \ud83c\udff4\udb40\udc67\udb40\udc62\udb40\udc77\udb40\udc6c\udb40\udc73\udb40\udc7f

            ./bin/emoji_process.py https://unicode.org/emoji/charts/full-emoji-list.html | wc -l
1816

            ./bin/emoji_translate.py flag_wales U+1F3F4 U+E0067 U+E0062 U+E0077 U+E006C U+E0073 U+E007F
NAME: flag_wales	 CODELIST: ['U+1F3F4', 'U+E0067', 'U+E0062', 'U+E0077', 'U+E006C', 'U+E0073', 'U+E007F']
NAME: flag_wales	 CONVERTED: \ud83c\udff4\udb40\udc67\udb40\udc62\udb40\udc77\udb40\udc6c\udb40\udc73\udb40\udc7f

To Do List:
===========

* Add output into CSV and other formats

Authors
=======

* Mat Gritt (mat@sumologic.com)
* Wayne Kirk Schmidt (wschmidt@sumologic.com)

