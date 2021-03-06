<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Transaction</title>
    <link rel="stylesheet" type="text/css" href="/images/datepicker.css" />
    <script type="text/javascript" src="/images/datepicker.js"></script>
</head>
<body>
% include('header.html')

<h1>Zhima - Transaction</h1>
<form method="POST" id="form" action="/transaction/add">
<table>
    % ro_fields = ('id', 'member_id', 'created_on')
    % for k,v in transaction.data.items():
    <tr><td style="text-align:right">{{k.replace('_', ' ').capitalize()}}</td>
        % if k == 'type':
        <td><select id="type" name="type" {{" readonly" if read_only or k in ro_fields else ""}} onchange="onChangeType(this)">
            % for m in transaction.MEMBERSHIP:
                <option value="{{m[0]}}">{{m[1]}}</option>
            %end
        </select></td>
        % else:
        <td><input type="text" size="40" value="{{v}}" name="{{k}}" id="{{k}}"{{" readonly" if read_only or k in ro_fields else ""}}
            % if k in ("valid_from", "valid_until"):
            class='datepicker' title='YYYY-MM-DD'
            % end
            /></td></tr>
        % end
    % end
</table>
    % if transaction.data.get('id') is None:
    <p><input type="submit" value="Post" name="submit" /></p>
    % elif not read_only:
    <p><input type="submit" value="Update" name="submit" /></p>
    % end
</form>
% if "member_id" in transaction.data:
<p>Back to this <a href="/member/{{transaction.data['member_id']}}">member's information page</a></p>
% end
<script type="text/javascript" language="javascript">
window.addEventListener("load",function(){
    document.getElementById("type").value = "{{transaction.data.get("type", "")}}";
},false);

function onChangeType(selectType)
{
    var value = selectType.value;
    var valid_from = new Date(Date.parse(document.getElementById("valid_from").value));
    if (value=="1M MEMBERSHIP")
    {
        valid_from.setDate(valid_from.getDate() + 31);
        document.getElementById("valid_until").value = valid_from.toISOString().substr(0,10);
        document.getElementById("amount").value = 200.00;
    }
    else if (value=="6M MEMBERSHIP")
    {
        valid_from.setDate(valid_from.getDate() + 181);
        document.getElementById("valid_until").value = valid_from.toISOString().substr(0,10);
        document.getElementById("amount").value = 900.00;
    }
    else if (value=="10 ENTRIES")
    {
        valid_from.setDate(valid_from.getDate() + 181);
        document.getElementById("valid_until").value = valid_from.toISOString().substr(0,10);
        document.getElementById("amount").value = 350.00;
    }
    else if (value=="DONATION")
    {
        valid_from = new Date(Date.parse("9999-12-31"));
        document.getElementById("valid_until").value = valid_from.toISOString().substr(0,10);
    }
}
</script>
</body>
</html>