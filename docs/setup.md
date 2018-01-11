
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

Bluetooth with Python
---------------------
- https://github.com/karulis/pybluez
- toggleglobalsitepackages

sudo apt-get install python3-bluez

??? pip install pybluez[ble]

**or**

sudo apt-get update
sudo apt-get install python-pip python-dev ipython

sudo apt-get install bluetooth libbluetooth-dev
sudo pip install pybluez



