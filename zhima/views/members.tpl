<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zhima - Member List</title>
</head>
<body>
% include('header.html')
<h1>XCJ Members</h1>
<p>
<fieldset>
    <legend>Operations:</legend>

Status:
  <select id = "status_list"
    onchange = 'window.location = this.value=="ALL" ? "/members" : "/members?filter=" + this.value;'>
    <option value = "ALL">All</option>
    <option value = "OK">OK</option>
    <option value = "NOT_OK">Not OK</option>
    <option value = "INVALID">Invalid</option>
  </select>

  &nbsp;
  &nbsp;
  &nbsp;
  &nbsp;

  <input type="text" name="search" id
  ="search" size="20" placeholder="Search"/>

  &nbsp;
  &nbsp;
  &nbsp;

<input type='button' id='new' value='New Member' onClick='window.location = "/members/new"'>
</fieldset></p>
<script>
const urlParams = new URLSearchParams(window.location.search);
const myParam = urlParams.get('filter');
if (myParam)
{
    document.getElementById("status_list").value = myParam;
}

document.addEventListener('keyup', function (event) {
    var key = event.key || event.keyCode;
    if (key=='Enter' || key==13)
    {
        var searchStr = document.getElementById("search").value;
        if (searchStr)
            window.location = "/members?search="+searchStr;
    }
});
</script>

% if len(rows):
%   columns=("id", "rfid", "username", "email", "status", "role", "city", "last_active_type", "last_active_time", "create_time")
<table>
        <tr>
            % for k in columns:
            <th>{{k.replace('_', ' ').title()}}</th>
            % end
        </tr>
        % for row in rows:
        <tr>
            % for k, v in [ (_k,_v) for _k, _v in row.items() if _k in columns]:
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