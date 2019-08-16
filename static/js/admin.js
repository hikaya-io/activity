$(document).ready(function() {
	$('#userTable').DataTable();

	$('#id_user_email_list').select2({
		theme: 'bootstrap',
		tags: true,
	});
	$('#id_organization').select2({
		theme: 'bootstrap',
	});
});

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
			toastr.success(
				'Admin configurations have been successfuly updated',
				'Succesfully Updated'
			);
		},
		error: function(xhr, desc, error) {
			toastr.error('An error occured during the operation', 'An Error occurred');
		},
	});

	return false;
});

$('form#inviteUserForm').submit(e => {
	e.preventDefault();
	e.stopImmediatePropagation();
	// get all the inputs into an array.
	var $inputs = $('#inviteUserForm :input');

	// get an associative array of just the values.
	var values = {};
	$inputs.each(function() {
		values[this.name] = $(this).val();
	});

	// validate emails
	let isEmailValid = true;

	values.user_email_list.forEach(element => {
		if (!validateEmail(element)) {
			isEmailValid = false;
			toastr.error(`The email [${element}] is invalid`, 'Invalid Email Address');
		}
	});

	const data = {
		user_email_list: values.user_email_list,
		organization: values.organization,
		csrfmiddlewaretoken: values.csrfmiddlewaretoken,
	};
	if (isEmailValid) {
		$.ajax({
			url: '/accounts/admin/invite_user/',
			type: 'POST',
			data,
			success: function(res, status) {
				if (res) {
					toastr.success(
						`You have successfuly invited ${data.user_email_list.length} user(s)`,
						'Inviattion Successful'
					);

					setTimeout(() => {
						window.location.reload();
					}, 2000);
				}
			},
			error: function(xhr, desc, error) {
				toastr.error('An error occured during the operation', 'An Error occurred');
			},
		});
	}
});

/**
 * validate email list
 */
function validateEmail(email) {
	var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	return re.test(String(email).toLowerCase());
}
