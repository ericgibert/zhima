<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima</title>
</head>
<body>
% include('header.html')
<h1>Dashboard for Zhima</h1>


% from zhima import __version__, __author__, __license__
<p>Version: {{__version__}}<br/>
   Author: &nbsp;{{__author__}}<br/>
   License: {{__license__}}<br/>
</p>
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
<table border="1">
% for row in rows:
    <tr><td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td></tr>
%end
</table>

<p>
<hr/>
% if session_valid:
<b><a href="/restart">Restart</a></b> the application.
<hr/>
To stop the application, click <a href="/stop">here</a>.
% end
</p>
</body>
</html>