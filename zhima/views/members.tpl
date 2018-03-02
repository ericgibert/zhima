<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Member List</title>
</head>
<body>
% include('header.html')
<h1>XCJ Members</h1>
<p>You can add a filter by 'status' on the URL like so: <a href="/members?filter=OK">/members?filter=OK</a></p>
<p>You can create a new member here: <a href="/members/new">/members/new</a></p>
% if len(rows):
<table>
        <tr>
            % for k in rows[0].keys():
            <th>{{k}}</th>
            % end
        </tr>
        % for row in rows:
        <tr>
            % for k, v in row.items():
            <td>{{!"""<a href="/member/{0}">{0}</a>""".format(v) if k=='id' else v}}</td>
            % end
        </tr>
        % end
</table>
<p>
% if current_page > 0:
    <a href="/members/{{current_page-1}}{{req_query}}">Previous</a>
% end
% if len(rows) == 25:
    <a href="/members/{{current_page+1}}{{req_query}}">Next</a>
% end

% else:
    <h2>Sorry, no rows found.</h2>
% end

</p>
</body>
</html>