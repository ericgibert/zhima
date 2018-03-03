<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Member</title>
</head>
<body>
% include('header.html')
<h1>Zhima - Member {{member.data['username']}} ({{member.data['id']}})</h1>

% if read_only:
% from time import time
<img src="/images/XCJ_{{member.data['id']}}.png?{{time()}}"/>
% else:
<script>
    function check_pass() {
    document.getElementById('submit').disabled =
        (document.getElementById('passwd').value !=
            document.getElementById('passwdchk').value);
    }
    function validate_me() {
      if (document.forms["form"]["passwd"].value=="") {
        alert("Password cannot be be blank");
        return false;
      }
      if (!isValidDate(document.forms["form"]["birthdate"].value)) {
        alert(document.forms["form"]["birthdate"].value + " is not a valid birth date in the format YYYY-MM-DD");
        return false;
      }
    }
    function isValidDate(date) {
        var temp = date.split('-');
        var yyyy = Number(temp[0]);
        var mm = Number(temp[1]);
        var dd = Number(temp[2]);
        var d = new Date(yyyy, mm-1, dd);
        return d && (d.getMonth() + 1)==mm && d.getDate()==dd && d.getFullYear()==yyyy;
    }
</script>
<form method="POST" id="form" action="/member/edit/{{member.data['id']}}" onsubmit="return validate_me()">
% end
% if session['id']!=member.data['id']:
<p>You are logged as {{session['name']}} ({{session['id']}})</p>
% end

<table style="border: 3px solid black;">
    % for k,v in member.data.items():
    <tr><td style="text-align:right; border: 0px;">{{k.capitalize()}}</td>
        <td style="border: 0px;">
            <input type={{!'"password"' if k.startswith('passwd') else '"text"'}} size="40" value="{{v}}" name="{{k}}" id="{{k}}"
                   {{"readonly" if read_only or k=='id' else ""}}
                   {{!"onchange='check_pass();'" if k.startswith('passwd') else ""}}
            />
        </td></tr>
    % end
    % if session['admin']:
    <tr><td style="border: 0px;"> </td>
        <td style="border: 0px;">
            % if read_only:
            <button type="button" onclick="location.href='/member/edit/{{member.data['id']}}'">Edit</button>
            % else:
            <input type="submit" value="Submit" name="submit" id="submit" {{ "disabled" if member.data['id']==0 else ''}}/>
            % end
        </td></tr>
    % end
</table>

%if not read_only:
</form>
% elif session['admin']:
<p>
    Add a <a href="/transaction/{{member.data['id']}}">new transaction</a>
</p>
% end

% if read_only:
    % if member.transactions:
    <style>
    table, td {
    border: 1px solid black;
    }
    </style>
    <p><table>
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
    </table></p>
    % else:
    <h2>No transactions recorded for this member</h2>
    % end
% end
</body>
</html>