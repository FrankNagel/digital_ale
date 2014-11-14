<%page expression_filter="h"/>
<%inherit file='base.mako' />
% if failed_attempt:
<p><font color="red">Invalid credentials, try again.</font></p>
% endif
<form method="post" action="${ request.path }">
<p>
<label for="login">Login</label><br>
<input type="text" name="login_name" value="${ login_name }">
</p>
<p>
<label for="passwd">Password</label><br>
<input type="password" name="password">
</p>
<input type="hidden" name="next" value="${ url_next }">
<input type="submit" name="submit" value="Login">
</form>
