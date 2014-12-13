#!/bin/sh
cd `dirname $0`/../src

OLD=`cat ./addon.xml | grep '<addon' | grep 'version="' | grep -E -o 'version="[0-9\.]+"' |  grep -E -o '[0-9\.]+'`
echo "Old version: $OLD"
echo -n 'New version: '
read NEW

sed -e "s/fm\" version=\"$OLD\"/fm\" version=\"$NEW\"/g" ./addon.xml > ./addon2.xml
mv ./addon2.xml ./addon.xml

rm -rf ../plugin.audio.lovifm
rm -f ./plugin.audio.lovifm.zip
mkdir ../plugin.audio.lovifm
cp -r ./* ../plugin.audio.lovifm/

cd ../
zip -rq ./plugin.audio.lovifm.zip ./plugin.audio.lovifm

cp ./plugin.audio.lovifm.zip ../repository.hal9000/repo/plugin.audio.lovifm/plugin.audio.lovifm-$NEW.zip

rm -rf ./plugin.audio.lovifm
rm -f ./plugin.audio.lovifm.zip

`../repository.hal9000/build/build.sh`
