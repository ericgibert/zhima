<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - {{"Group" if member['role'] == 4 else "Member"}}</title>
</head>
<body>
% include('header.html')
<h1>Zhima - {{"Group" if member['role'] == 4 else "Member"}} {{member['username']}} ({{member['id']}})</h1>

% if read_only:
% from time import time
    <p>
    % if member['role'] == 4:
    <img src="/images/emoji-group-event.jpg"/>
    % elif member.qrcode_is_valid:
    <img src="/images/XCJ_{{member.data['id']}}.png?{{time()}}"/>
        % if member['email']:
            <a href="/member/email_qrcode/{{member['id']}}">Email the QR code</a>
        % end
    % else:
    <img src="/images/emoji-not-happy.jpg"/>
    % end
    </p>
% else:
<link rel="stylesheet" type="text/css" href="/images/datepicker.css" />
<script type="text/javascript" src="/images/datepicker.js"></script>
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
      //if (!isValidDate(document.forms["form"]["birthdate"].value)) {
      //  alert(document.forms["form"]["birthdate"].value + " is not a valid birth date in the format YYYY-MM-DD");
      //  return false;
      //}
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
<form method="POST" id="form" action="/member/edit/{{member.data.get('id', 0)}}" onsubmit="return validate_me()">
% end
% if session['user']['id']!=member.data.get('id', 0):
<p>You are logged as {{session['user']['name']}} ({{session['user']['id']}})</p>
% end

<table style="border: 3px solid black;">
    % ALWAYS_RO=('id', 'create_time', 'last_update', 'last_active_type', 'last_active_time')
    % for k,v in member.data.items():
    <tr><td style="text-align:right; border: 0px;">{{k.replace('_', ' ').capitalize()}}</td>
        <td style="border: 0px;">
            % if k == 'gender':
                <select id="gender" name="gender" {{"disabled" if read_only else ""}}>
                <option value="0" {{"selected" if v==0 else ""}}>Unassigned</option>
                <option value="1" {{"selected" if v==1 else ""}}>Male</option>
                <option value="2" {{"selected" if v==2 else ""}}>Female</option>
                <option value="5" {{"selected" if v==5 else ""}}>Event</option>
                </select>
            % elif k == 'status':
                <select id="status" name="status" {{"disabled" if read_only else ""}}>
                % for ks,vs in member.STATUS.items():
                <option value="{{ks}}" {{"selected" if v==ks else ""}}>{{vs}}</option>
                % end
                </select>
            % elif k == 'role':
                <select id="role" name="role" {{"disabled" if read_only else ""}}>
                % for kr,vr in member.ROLE.items():
                <option value="{{vr}}" {{"selected" if v==vr else ""}}>{{kr.capitalize()}}</option>
                % end
                </select>
            % else:
                <input type={{!'"password"' if k.startswith('passwd') else '"text"'}} size="40" value="{{v}}" name="{{k}}" id="{{k}}"
                       {{"readonly" if read_only or k in ALWAYS_RO else ""}}
                       {{!"onchange='check_pass();'" if k.startswith('passwd') else ""}}
                % if k in ("birthdate", ):
                class='datepicker' title='YYYY-MM-DD'
                % end
                />
            %end
        </td></tr>
    % end
    % if session['user'] and session['user'].is_staff:
    <tr><td style="border: 0px;"> </td>
        <td style="border: 0px;">
            % if read_only:
            <button type="button" onclick="location.href='/member/edit/{{member.data['id']}}'">Edit</button>
            % else:
            <input type="submit" value="Submit" name="submit" id="submit" {{ "disabled" if member.data.get(id', 0)==0 else ''}}/>
            % end
        </td></tr>
    % end
</table>

%if not read_only:
</form>
% elif session['user'] and session['user'].is_staff:
<p>
    Add a <a href="/transaction/{{member.data['id']}}">new transaction</a> or upload an associated file:
    <p style="">
    <form action="/upload/{{member.data['id']}}" method="post" enctype="multipart/form-data">
      Select a file: <input type="file" name="upload" />
      <input type="submit" value="Start upload" />
    </form>
    </p>
</p>
% end

% if read_only:
<hr>
    % if member.transactions:
    <p>Membership valid until {{member["validity"]}}</p>
    % if member["role"]==0:
        <h3>Registered entries:</h3>
        <ol>
        % for open in member.opens:
           <li>{{open}}</li>
        % end
        </ol>
    % end
    <style>
    table, td {
    border: 1px solid black;
    }
    </style>
    <p><table>
        <tr>
        % for k in member.transactions[0].keys():
        <th>{{k.replace('_', ' ').capitalize()}}</th>
        % end
        % for row in member.transactions:
        </tr><tr>
            % for k, v in row.items():
                %if k=='id' and session['user'] and session['user'].is_staff:
                <td><a href="/transaction/update/{{v}}">{{v}}</a></td>
                %else:
                <td>{{v}}</td>
                %end
            % end

            % if member["status"] == "OK" and member["gender"] == 5:
            <td><a href="/transaction/qrcode/{{row['id']}}"><img src="/images/qr-code-icon.jpg" style="width:20px;height:20px;border:0;"></a></td>
            % end
        </tr>
        % end
    </table></p>
    % else:
    <h2>No transactions recorded for this member</h2>
    % end
<hr>
<table style="border: 0px solid black;">
    % for f in member.files:
    <tr>
    <td style="border: 0px solid black;"><img src="{{ "/images/Adobe-PDF-Document-icon.png" if f.lower().endswith("pdf") else "/images/camera-icon.png"   }}"></td>
    <td style="border: 0px solid black;"><a href="{{f}}">{{f}}</a></td>
    </tr>
    % end
</table>
% end
</body>
</html>