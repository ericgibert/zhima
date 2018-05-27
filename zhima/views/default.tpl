<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima</title>
</head>
<body>
% include('header.html')
<h1>Welcome {{session['user']['name'] if session.get('user') else ""}} to Zhima</h1>

<table>



</table>


% from zhima import __version__, __author__, __license__
<p>Version: {{__version__}}<br/>
   Author: &nbsp;{{__author__}}<br/>
   License: {{__license__}}<br/>
</p>




<hr/>
% if session.get('user') and session['user'].is_admin:
<ul>
% import sys
    <li>Python: {{sys.version}}</li>
% import pkg_resources
    <li>bottle: {{pkg_resources.get_distribution("bottle").version}}</li>
    <li>pymysql: {{pkg_resources.get_distribution("pymysql").version}}</li>
% try:
    <li>pigpio: {{pkg_resources.get_distribution("pigpio").version}}</li>
% except pkg_resources.DistributionNotFound:
    <li>pigpio: not installed</li>
</ul>

<p>

<b><a href="/restart">Restart</a></b> the application.
<hr/>
To stop the application, click <a href="/stop">here</a>.
% end
</p>
</body>
</html>