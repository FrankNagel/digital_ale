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
<h2>Concept ${concept.id}</h2>
<p><b>eng</b> ${concept.eng}<br><b>fra</b> ${concept.fra}</p>

<div class="concept_table_wrapper">
<table class="concept_table display compact">
<thead>
  <tr>
    <th>Scan</th>
    <th>Status</th>
  </tr>
</thead>
<tbody>
% for scan, sheet in sheetEntries:
<tr><td><a href="${request.route_url('sheet', concept_id=scan.concept_fkey, scan_name=scan.scan_name)}" target="ale_sheet">${scan.scan_name}</a></td><td>${sheet is None and 'MISSING' or sheet.status}</td></tr>
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
