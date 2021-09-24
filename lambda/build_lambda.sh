#!/usr/bin/env bash

umask 022

staging="/tmp/EmojiTools-Staging"
zipfile="/tmp/EmojiTools.Package.zip"

rm -f $zipfile

mkdir -p $staging/package

cp ./lambda_function.cfg $staging
cp ./lambda_function.py $staging
cp ./emojilookup.json $staging

cd $staging

pip3 install --target ./package requests
pip3 install --target ./package argparse
pip3 install --target ./package configparser
pip3 install --target ./package bs4

cd $staging/package

zip -r $zipfile .

cd $staging

zip -g $zipfile ./lambda_function.cfg
zip -g $zipfile ./lambda_function.py
zip -g $zipfile ./emojilookup.json
