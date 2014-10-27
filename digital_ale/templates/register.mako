<%inherit file='base.mako' />
% if success_msg:
<p style='color: green'>${ success_msg }</p>
% endif
% if error_msg:
<p style='color: red'>${ error_msg }</p>
% endif
<form method="post" action="${ request.path }">
<p>
<label for="login_name">Login</label><br>
<input type="text" name="login_name" value="${ login_name }">
</p>
<p>
<label for="email">Email (not used at the moment, enter a valid one anyway)</label><br>
<input type="text" name="email" value="${ email }">
</p>
<p>
<label for="password">Password</label><br>
<input type="password" name="password">
</p>
<p>
<label for="confirm_password">Confirm Password</label><br>
<input type="password" name="confirm_password">
</p>
<input type="hidden" name="next" value="${ next }">
<input type="submit" name="submit" value="Register">
</form>
