<%page expression_filter="h"/>
<%inherit file='base.mako' />
<%block name="header">
  <link rel="stylesheet"
	href="http://code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css"
	type="text/css">
  <script type="text/javascript" src="http://code.jquery.com/jquery-2.1.1.js"></script>
  <script type="text/javascript"
	  src="http://code.jquery.com/ui/1.10.4/jquery-ui.js"></script>
  <script type="text/javascript" src="/static/sheet.js"></script>
</%block>
<form method='post' action='${ req.url }'>
  <div id='overlay' style="float:left; position: relative; height:1132px;
			   width:802px; display:inline-block; background-color:#F5F5F5">
    <div id='rendered-view' style="position: absolute; top:0; left:0; height:1132px; display:inline-block">
      <canvas height='1130' width='800px' id='canvas' style='height:1130px;
	      width:800px; overflow:hidden; background-color:#F5F5F5; border:1px solid #000000;'>
      </canvas>
    </div>
    <div id='ale-scan' class='ale-scan'>
        <div id='ale-scan-bg' class='ale-scan-bg' style="background-image: url(${'/static/scans/' + scan.get_path_to_file() });">
        </div>
    </div>
    <div class=overlay-button><input type="button" id='rotate' value='Rotate' /></div>
  </div>
  <div id="slider-vertical" style="float:left; height:1132px;
				   display:inline-block; margin-right:10px"></div>
  <div style="float: left; height:1132px; display:inline-block">
    <input type="button" id="refresh" value='Refresh' />
    Status:
    <select name="status">
% for o in sheetEntryState:
<%
    selected = ((sheetEntry is None and o=='In Progress' or (sheetEntry is not None and sheetEntry.status == o)) and "selected") or ''
%>
    <option value="${o}" ${ selected }>${o}</option>
% endfor
    </select>
    <input type="submit" name="submit" value='Save' />
% if message:
    ${ message }
% endif
    <br>
    <textarea id='sheet_text' name='data' style="margin-top:10px; height:66%;
    width:600px" spellcheck='false'></textarea>
    <p>Comment<br>
    <textarea id='sheet_comment' name='comment' style="margin-top:10px; height:20ex; width:600px"
	      spellcheck='false'>
% if sheetEntry:
${sheetEntry.comment}
% endif
    </textarea>
    </p>
  </div>
</form>
<%block name="js_footer">
<%
if sheetEntry:
    innerHtml = sheetEntry.js_escaped_data()
else:
    innerHtml = ''
%>
<script type="text/javascript">
  $(document).ready(function(){
    document.getElementById('sheet_text').innerHTML = '${ innerHtml | n }';
    refresh_canvas();
  });
</script>
</%block>
