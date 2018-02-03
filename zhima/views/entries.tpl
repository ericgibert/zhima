<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Entries</title>
</head>
<body>
% include('header.html')
<h1>Entries @ XCJ</h1>
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
    <a href="/entries/{{current_page-1}}">Previous</a>
    % end
    % if len(rows) == 25:
    <a href="/entries/{{current_page+1}}">Next</a>
    % end
</p>
</body>
</html>