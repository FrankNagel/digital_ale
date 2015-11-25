<%page expression_filter="h"/>
<%inherit file='base.mako' />
<%block name="header">
  <link rel="stylesheet"
        href="http://code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css"
        type="text/css">

  <script type="text/javascript" src="http://code.jquery.com/jquery-2.1.1.js"></script>
</%block>

<h2>User ${user.login_name}</h2>

<p>
<form method="post" action="${ request.path }">
  <fieldset>
    <legend>Set Password</legend>
    <input type="password" name="password">
    <input type="hidden" name="action" value="save_password">
    <input type="submit" name="submit" value="Save">
  </fieldset>
</form>
</p>

<p>
<form method="post" action="${ request.path }">
  <fieldset>
    <legend>Manage Roles</legend>
%for role in roles:
    <label for="${role}">${role}</label>
    <input type="checkbox" name="${role}" value="selected" ${"checked" if (user.roles and role in user.roles) else ''}><br/>
%endfor
    <input type="hidden" name="action" value="save_roles">
    <input type="submit" name="submit" value="Save">
  </fieldset>
</form>
</p>



