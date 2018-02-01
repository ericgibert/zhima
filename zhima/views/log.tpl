<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Log</title>
</head>
<body>
% include('header.html')
<h1>Log</h1>
<p>You can add a filter by log_type on the URL</p>
<table border="1">
    <tr><th>log_id</th><th>Log Type</th><th>Code</th><th>Message</th><th>Created on</th></tr>
% for row in rows:
<tr><td>{{row[0]}}</td>
    <td>{{row[1]}}</td>
    <td>{{row[2]}}</td>
    <td>{{row[3]}}</td>
    <td>{{row[4]}}</td>
% end
</table>
<p>
% if current_page > 0:
    <a href="/log/{{current_page-1}}{{req_query}}">Previous</a>
% end
% if len(rows) == 25:
    <a href="/log/{{current_page+1}}{{req_query}}">Next</a>
% end
</p>
</body>
</html>