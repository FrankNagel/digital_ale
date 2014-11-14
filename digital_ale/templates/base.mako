<%page expression_filter="h"/>
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <link rel="stylesheet" href="/static/ale.css" type="text/css">
  <%block name="header"/>
</head>
<body>
<div class='header'>
<div><a class='home' href='/'>Digital ALE - Atlas Linguarum Europae</a></div>
<div class='header_spacer'></div>
% if username:
<div>Logged in as ${ username }. <a href='${ request.route_url('logout') }'>Logout</a></div>
% else:
<div>
<a href='${ request.route_url('login') + '?next=' + (url_next or request.url) }'>Login</a> or 
<a href='${ request.route_url('register') }'>Register</a>
</div>
% endif
</div>
<div class='body'>
${ next.body() }
</div>
<div class='footer'>
<%block name="footer"/>
</div>
<%block name="js_footer"/>
</body>
</html>

