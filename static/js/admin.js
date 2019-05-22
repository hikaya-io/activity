$(document).ready(function() {});

$('form#configForm').submit(function(e) {
	e.preventDefault();
	e.stopImmediatePropagation();
	const form = $(this);
	const data = form.serializeArray().reduce(function(obj, item) {
		obj[item.name] = item.value;
		return obj;
	}, {});
	$.ajax({
		url: '/accounts/admin/configurations',
		type: 'POST',
		data,
		success: function(data, status) {
			console.log('Data', data);
			console.log('Status', status);
		},
		error: function(xhr, desc, error) {
			console.log(error)
		},
	});

	return false;
});
