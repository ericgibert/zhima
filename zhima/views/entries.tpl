<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Entries</title>
</head>
<body>
% include('header.html')
<h1>Entries @ XCJ</h1>

<table border="1">
% for row in rows:
    <tr><td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td></tr>
%end
</table>

</body>
</html>