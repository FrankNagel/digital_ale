<%page expression_filter="h"/>
<%inherit file='base.mako' />
<%block name="header">
  <link rel="stylesheet"
        href="http://code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css"
        type="text/css">

  <script type="text/javascript" src="http://code.jquery.com/jquery-2.1.1.js"></script>
</%block>

<h2>Import Sheets</h2>
% if success_msg:
<p style='color: green'>${ success_msg }</p>
% endif
% if error_msg:
<p style='color: red'>${ error_msg }</p>
% endif
<form method="post" action="${ request.path }" accept-charset="utf-8" enctype="multipart/form-data">
  <fieldset>
    <legend>ZIP archive or TEXT file</legend>
    <input type="file" name="sheet" value=""><br>
    <input type="submit" name="submit" value="Upload">
  </fieldset>
</form>
% if import_msg:
<p>
<pre>
${import_msg}
</pre>
</p>
% endif

