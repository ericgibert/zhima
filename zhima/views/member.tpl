<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima</title>
</head>
<body>
% include('header.html')

<h1>Zhima - Member</h1>
<img src="/images/XCJ_{{member.data['id']}}.png"/>
<style>
table, td {
border: 0px;
padding: 5px;
text-align: left;
}
</style>
<table>
    % for k,v in member.data.items():
    <tr><td style="text-align:right">{{k}}:</td>
        <td><input type="text" size="40" value="{{v}}" name="{{k}}"{{" readonly" if read_only else ""}}/></td></tr>
    % end
</table>

</body>
</html>