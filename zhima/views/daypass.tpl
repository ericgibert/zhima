<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Daypass</title>
    <link rel="stylesheet" type="text/css" href="/images/datepicker.css" />
    <script type="text/javascript" src="/images/datepicker.js"></script>
</head>
<body>
% include('header.html')
<h1>Zhima - Daypass</h1>
% if session['user'] and session['user'].is_staff:
<script>
    function validate_me() {
      if (!isValidDate(document.forms["form"]["from_date"].value)) {
        alert(document.forms["form"]["from_date"].value + " is not a valid date in the format YYYY-MM-DD");
        return false;
      }
      if (document.forms["form"]["until_date"].value!="" and !isValidDate(document.forms["form"]["until_date"].value)) {
        alert(document.forms["form"]["until_date"].value + " is not a valid date in the format YYYY-MM-DD");
        return false;
      }
      if (document.forms["form"]["from_date"].value > document.forms["form"]["until_date"].value) {
        alert("The 'From' date cannot greater then the 'Until' date");
        return false;
      }
    }

    function assign_until_date() {
        document.forms["form"]["until_date"].value = document.forms["form"]["from_date"].value;
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
<form method="POST" id="form" action="/daypass" onsubmit="return validate_me()">
    % if period[1]:
    <p>As Admin: from 1 to 7 days pass only</p>
    % else:
    <p>As staff: single day pass only</p>
    % end
    <table style="border: 1px solid black;">
        <tr><td>From</td>
            <td><input type="text" size="20" value="{{period[0]}}" name="from_date" id="from_date" class='datepicker'
                       title='YYYY-MM-DD'
                       onchange='assign_until_date();'/></td>
        </tr>
        <tr><td>Until</td>
            <td><input type="text" size="20" value="{{period[1]}}" name="until_date" id="until_date"
                       {{!"class='datepicker' title='YYYY-MM-DD'" if period[1] else "disabled"}} /></td>
        </tr>
        % if qr_code:
        <tr><td>QR Code</td><td><img src="{{qr_code}}"></td></tr>
        <tr><td>Email QRCode to</td><td><input type="text" size="40" value="" name="email" id="email"/></td></tr>
        % end
    </table>
    <p><input type="submit" value="Submit" name="submit" /></p>
</form>
% else:
<h2>Only Staff can access this page and generate daypasses.</h2>
% end
</body>
</html>