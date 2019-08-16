mkdir -p temp


apt update -y
apt install locales
apt install -y python3 python3-pip
apt install -y  libgdal-dev libgdal20
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
ls /usr/include/gdal
gdal-config --version
echo $LANG
pip3 install -r requirements.txt
