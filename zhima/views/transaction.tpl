<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Transaction</title>
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
        <td><select id="type" name="type" {{" disabled" if read_only or k in ro_fields else ""}} >
            <option value="1M MEMBERSHIP">1 month membership</option>
            <option value="6M MEMBERSHIP">6 months membership</option>
            <option value="DONATION">Donation</option>
            <option value="EVENT">Event</option>
            <option value="TOOL">Tool Usage</option>
            <option value="CROWD FUNDING">Crowd Funding</option>
        </select></td>
        % else:
        <td><input type="text" size="40" value="{{v}}" name="{{k}}"{{" readonly" if read_only or k in ro_fields else ""}}/></td></tr>
        % end
    % end
</table>
    % if transaction.data['id'] is None:
    <p>&nbsp;&nbsp;&nbsp;<input type="submit" value="Post" name="submit" /></p>
    % end
</form>
<script type="text/javascript" language="javascript">
window.addEventListener("load",function(){
    document.getElementById("type").value = "{{transaction.data["type"] if "type" in transaction.data else ""}}";
},false);

function get_value(pwo_cls, id)
{
    var xhttp = new XMLHttpRequest();
    var url = "/" + pwo_cls + "/value/" + id;
    xhttp.open("GET", url, true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            var response = JSON.parse(this.responseText);
            var msg = "<p>this.value = " + response["value"] + "</p><hr/>"
                    + "<p>['if']: " + response["if"] + "</p><p>make: " + response["make"]
                    + "</p><p>eval = " + response["eval"] + "</p>";
            document.getElementById('value_text').innerHTML = msg;
        }
    }
    xhttp.send();
}
</script>
</body>
</html>