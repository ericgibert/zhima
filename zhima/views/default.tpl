<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima</title>
</head>
<body>
% include('header.html')
<h1>Welcome {{session['user']['name'] if session.get('user') else ""}} to Zhima</h1>

% from zhima import __version__, __author__, __license__
% from http_view import __version__ as http_version
<p>Version: {{__version__}}<br/>
    HTTP: {{http_version}}<br/>
   Author: &nbsp;{{__author__}}<br/>
   License: {{__license__}}<br/>
</p>

<hr/>
% if session.get('user') and session['user'].is_admin:
<ul>
% import sys
    <li>Python: {{sys.version}}</li>
% import pkg_resources
% try:
    <li>bottle: {{pkg_resources.get_distribution("bottle").version}}</li>
    <li>pymysql: {{pkg_resources.get_distribution("pymysql").version}}</li>
    <li>pigpio: {{pkg_resources.get_distribution("pigpio").version}}</li>
% except pkg_resources.DistributionNotFound:
    <li>some packages version not found</li>
</ul>

% if session['user'].is_admin:
<P>
    Whitelist of servers able to use API:
<ul>
    % for wls in controller.db.access['whitelist']:
    <li>{{wls}}</li>
    % end
</ul>
</P>
% end
<p>
<b><a href="/restart">Restart</a></b> the application.
<hr/>
To stop the application, click <a href="/stop">here</a>.
% end
</p>
</body>
</html>