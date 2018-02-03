<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Member</title>
</head>
<body>
% include('header.html')

<h1>Zhima - Member</h1>
<img src="/images/XCJ_{{member.data['id']}}.png"/>
<table style="border: 3px solid black;">
    % for k,v in member.data.items():
    <tr><td style="text-align:right; border: 0px;">{{k.capitalize()}}</td>
        <td style="border: 0px;"><input type="text" size="40" value="{{v}}" name="{{k}}"{{" readonly" if read_only else ""}}/></td></tr>
    % end
</table>
<p>
    Add a <a href="/transaction/{{member.data['id']}}">new transaction</a>
</p>

% if member.transactions:
<style>
table, td {
border: 1px solid black;
}
</style>
<table>
    <tr>
    % for k in member.transactions[0].keys():
    <th>{{k}}</th>
    % end
    % for row in member.transactions:
    </tr><tr>
        % for v in row.values():
        <td>{{v}}</td>
        % end
    </tr>
    % end
</table>
% else:
<h2>No transactions recorded for this member</h2>
% end

</body>
</html>