
make environment **zhima**
--------------------------

Install prerequisites.

    sudo apt-get install python3 python3-pip virtualenvwrapper
    
Create a Python3 based virtual environment. Optionally **enable** --system-site-packages flag.

    mkvirtualenv -p /usr/bin/python3 <venv-name>
    
Set into the virtual environment.

    workon <venv-name>
    
Install other requirements using pip package manager.

    pip install -r requirements.txt
    pip install <package_name>
    
When working on multiple python projects simultaneously it is usually recommended to install common packages like Django globally and then reuse them in virtualenvs.

Using this technique saves a lot of time spent on fetching packages and installing them, apart from consuming minimal disk space and network bandwidth.

    sudo -H pip3 -v install Django
    mkvirtualenv -p $(which python3) --system-site-packages <venv-name>

Global libraries
----------------

- workon zhima
- pip install requests
- pip install pigpio

and do not forget to run: `sudo pigpiod` before the first execution


QR code libraries
-----------------


````
    sudo dnf install zbar-devel   
````


- pip install zbarlight  # to read a QR code from an image
- pip install qrcode  # to create a QR code

- https://pypi.python.org/pypi/zbarlight
- https://pypi.python.org/pypi/qrcode


Camera control
--------------
- pip install opencv-python
- https://pypi.python.org/pypi/opencv-python

- pip install picamera

Bluetooth with Python
---------------------

pip install gatt
- https://github.com/karulis/pybluez
- toggleglobalsitepackages

sudo apt-get install python3-bluez

??? pip install pybluez[ble]

**or**

    sudo apt-get update
    sudo apt-get install python-pip python-dev ipython

    sudo apt-get install bluetooth libbluetooth-dev
    sudo pip install pybluez


Actually done:
==============
    sudo apt-get install bluetooth libbluetooth-dev
    sudo apt-get install libglib2.0-dev
    sudo apt-get install python3-dbus
    sudo apt-get install libboost-thread-dev libboost-python-dev

    sudo pip3 install gatt gattlib
    sudo pip3 install pybluez pybluez[ble]



    hciconfig
    
If bluetooth device is DOWN:

    sudo rfkill unblock bluetooth
    sudo hciconfig  hci0 up

    sudo hcitool -i hci0 lescan

OpenCV
======
https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/

Bottle and Bottlesession
========================

    ---not yet  -----  pip3 install bottle   ---- need version >= 0.13 for PATCH
    cd Private
    git clone https://github.com/bottlepy/bottle.git
    cd bottle
    cp bottle.py  ~/.virtualenvs/zhima/lib/python3.6/site-packages

    git clone https://github.com/linsomniac/bottlesession.git
    cd bottlesession
    cp bottlesession.py  ~/.virtualenvs/zhima/lib/python3.6/site-packages
    ==> modifications of this module as describe in http_view.py 
    
    
Crypto
======

pip install pycrypto


Markdown
========

pip install markdown


MySQL
=====

pip install pymysql


Auto-start at boot
==================


> cat /lib/systemd/system/zhima.service

--------
    [Unit]
    Description=zhima service
    After=network.target multi-user.target
      
    [Service]
    Type=forking
    User=pi
    ExecStart=/home/pi/zhima/zhima/zhima.sh start 
 
    [Install]
    WantedBy=multi-user.target

--------

> sudo chmod 644 /lib/systemd/system/zhima.service

> sudo systemctl daemon-reload

> sudo systemctl enable zhima.service



