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

<h2>Overview</h2>
<p>Please note:</p>
<ul>
  <li>You need to create an account and log in to save any changes.</li>
  <li>Report any bugs or other issues on <a href="https://github.com/FrankNagel/digital_ale/issues">Github</a>.</li>
</ul>
<table class='overview_table display'>
<thead>
  <tr>
    <th>Concept</th>
    <th>English</th>
    <th>French</th>
    <th>Scans</th>
    <th>Unchecked</th>
    <th>Contains @</th>
    <th>In Progress</th>
    <th>Problematic</th>
    <th>OK</th>
    <th>Ignore</th>
    <th>Missing</th>
  </tr>
</thead>
<tbody>
% for r in overview:
  <tr>
  <td><a href=${request.route_url('concept', concept_id=r.id)}>${r.id}</a></td>
  <td>${r.eng}</td>
  <td>${r.fra}</td>
  <td>${r.num_scans}</td>
  <td>${r.num_unchecked}</td>
  <td>${r.num_contains_at}</td>
  <td>${r.num_in_progress}</td>
  <td>${r.num_problematic}</td>
  <td>${r.num_ok}</td>
  <td>${r.num_ignore}</td>
  <td>${r.num_missing}</td>
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

