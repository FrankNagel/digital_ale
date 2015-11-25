<%page expression_filter="h"/>
<%inherit file='base.mako' />
<%block name="header">
  <link rel="stylesheet"
        href="http://code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css"
        type="text/css">

  <script type="text/javascript" src="http://code.jquery.com/jquery-2.1.1.js"></script>
</%block>

<h2>Users</h2>
<ul>
%for name in user_list:
  <li><a href=${request.route_url('admin_user_settings', user_id=name)}>${name}</a></li>
</u>
%endfor


