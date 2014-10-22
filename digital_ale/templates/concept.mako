<%inherit file='base.mako' />
<h2>Concept ${concept.id}</h2>
<p><b>eng</b> ${concept.eng}<br><b>fra</b> ${concept.fra}</p>

<table class="concept_table">
<tbody>
% for scan, sheet in sheetEntries:
<tr><td><a href="${request.route_url('sheet', concept_id=scan.concept_fkey, scan_name=scan.scan_name)}" target="ale_sheet">${scan.scan_name}</td><td>${sheet is None and 'MISSING' or sheet.status}</td></tr>
% endfor
</tbody>
</table>

