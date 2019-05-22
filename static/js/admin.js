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
			toastr.success('Admin configurations have been successfuly updated', 'Succesfully Updated')
		},
		error: function(xhr, desc, error) {
			toastr.error( 'An error occured during the operation', 'An Error occurred')
		},
	});

	return false;
});
