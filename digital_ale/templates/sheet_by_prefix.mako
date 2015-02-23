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
<h2>Prefix ${sheet_prefix}</h2>
<p>
  <a href='${request.route_url('sheet_prefix_data', sheet_prefix=sheet_prefix)}'>Extracted Data</a><br>
</p>

<h3>Scans</h3>
<div class="concept_table_wrapper">
<table class="concept_table display compact">
<thead>
  <tr>
    <th>Concept</th>
    <th>Scan</th>
    <th>Status</th>
  </tr>
</thead>
<tbody>
% for scan, sheet in scans_sheets:
<tr><td><a href="${request.route_url('concept', concept_id=scan.concept_fkey)}">${scan.concept_fkey}</a></td><td><a href="${request.route_url('sheet', concept_id=scan.concept_fkey, scan_name=scan.scan_name)}">${scan.scan_name}</a></td><td>${sheet is None and 'MISSING' or sheet.status}</td></tr>
% endfor
</tbody>
</table>
</div>
<%block name="js_footer">
<script type="text/javascript">
  $(document).ready(function(){
    $('.concept_table').DataTable({
      paging: false
      });
  });
</script>
</%block>
