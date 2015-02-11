<%page expression_filter="h"/>
<%inherit file='base.mako' />
<%block name="header">
  <link rel="stylesheet"
        href="http://code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css"
        type="text/css">
  <link rel="stylesheet"
        href="//cdn.datatables.net/plug-ins/380cb78f450/integration/jqueryui/dataTables.jqueryui.css"
        type="text/css">

  <script type="text/javascript" src="http://code.jquery.com/jquery-2.1.1.js"></script>
  <script type="text/javascript" src="//cdn.datatables.net/1.10.3/js/jquery.dataTables.min.js"></script>
  <script type="text/javascript"
  	  src="//cdn.datatables.net/plug-ins/380cb78f450/integration/jqueryui/dataTables.jqueryui.js"></script>
</%block>
% if concept:
<h2>Concept ${concept.id}</h2>
% endif
% if have_messages:
<h3>Parser Messages</h3>
% for scan, sheet in scans_sheets:
% if sheet and sheet.parser_messages:
<a href='${request.route_url('sheet', concept_id=scan.concept_fkey, scan_name=scan.scan_name)}''>Sheet ${ '%i/%s' % (scan.concept_fkey, scan.scan_name) } </a>
<pre>
${sheet.parser_messages}
</pre>
% endif
% endfor
% endif
<h3>Extracted Data</h3>
<table class='overview_table display'>
<thead>
  <tr>
    <td>Pronounciation</td>
    <td>Pointcode_old</td>
    <td>Sheet</td>
 </tr>
</thead>
<tbody>
% for p, sheet_entry, scan in pronounciations:
  <tr>
    <td>${p.pronounciation}</td>
    <td>
% for place in p.observations:
${place.pointcode_old}
% endfor
</td>
    <td><a href='${request.route_url('sheet', concept_id=scan.concept_fkey, scan_name=scan.scan_name)}''>${ '%03i/%s' % (scan.concept_fkey, scan.scan_name) }</a></td>
  </tr>
% endfor
</tbody>
</table>

<%block name="js_footer">
<script type="text/javascript">
  $(document).ready(function(){
    $('.overview_table').DataTable({paging: false});
  });
</script>
</%block>
