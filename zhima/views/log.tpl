<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Log</title>
</head>
<body>
% include('header.html')
<h1>Log</h1>
<p>You can add a filter by 'type' on the URL like so: <a href="/log?filter=INFO">/log?filter=INFO</a></p>
% if len(rows):
<style>
table {
    border-collapse: collapse;
}

table, th {
    border: 1px solid black;
    padding: 5px;
    text-align: center;
}
table, td {
    border: 1px solid black;
    padding: 5px;
    text-align: left;
}
</style>
<table>
    <tr>
        % for k in rows[0].keys():
        <th>{{k}}</th>
        % end
    </tr>
% for row in rows:
    <tr>
    % for v in row.values():
    <td>{{v}}</td>
    % end
    </tr>
% end
</table>
<p>
% if current_page > 0:
    <a href="/log/{{current_page-1}}{{req_query}}">Previous</a>
% end
% if len(rows) == 25:
    <a href="/log/{{current_page+1}}{{req_query}}">Next</a>
% end
% else:
<h2>Sorry, no rows found.</h2>
% end
</p>
</body>
</html>