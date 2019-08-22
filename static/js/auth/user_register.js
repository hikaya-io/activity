$(document).ready(function() {
	// required fields
	$('#register_first_name').on('input', function() {
		const username = $(this);
		if (username.val()) {
			$('#div_first_name')
				.removeClass('has-error')
				.addClass('has-success');
		} else {
			$('#div_first_name')
				.removeClass('has-success')
				.addClass('has-error');
		}
	});

	$('#register_username').on('input', function() {
		const username = $(this);
		if (username.val()) {
			$('#div_username')
				.removeClass('has-error')
				.addClass('has-success');
		} else {
			$('#div_username')
				.removeClass('has-success')
				.addClass('has-error');
		}
	});

	// validate email address
	$('#register_email_address').on('input', function() {
		const emailAddressInput = $(this);
		const emailAddress = emailAddressInput.val();
		if (emailAddress && isValidEmail(emailAddress)) {
			$('#div_email_address')
				.removeClass('has-error')
				.addClass('has-success');
			$('#emailHelpBlock')
				.removeClass('hikaya-show')
				.addClass('hikaya-hide');
		} else if (emailAddress && !isValidEmail(emailAddress)) {
			$('#div_email_address')
				.removeClass('has-success')
				.addClass('has-error');
			$('#emailHelpBlock')
				.removeClass('hikaya-hide')
				.addClass('hikaya-show');
		} else {
			$('#div_email_address')
				.removeClass('has-success')
				.addClass('has-error');
			$('#emailHelpBlock')
				.removeClass('hikaya-hide')
				.addClass('hikaya-show');
		}
	});

	$('#register_password').keyup(function() {
		const password = $(this);
		$('#passwordHelpBlock').html(checkStrength(password.val()));
	});

	function checkStrength(password) {
		//initial strength
		var strength = 0;

		//if the password length is less than 6, return message.
		if (password.length < 6) {
			$('#div_password')
				.removeClass('has-success')
				.removeClass('has-warning')
				.addClass('has-error');
			return 'Password too short';
		}

		//length is ok, lets continue.

		//if length is 8 characters or more, increase strength value
		if (password.length > 7) strength += 1;

		//if password contains both lower and uppercase characters, increase strength value
		if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) strength += 1;

		//if it has numbers and characters, increase strength value
		if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/)) strength += 1;

		//if it has one special character, increase strength value
		if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) strength += 1;

		//if it has two special characters, increase strength value
		if (password.match(/(.*[!,%,&,@,#,$,^,*,?,_,~].*[!,",%,&,@,#,$,^,*,?,_,~])/)) strength += 1;

		//now we have calculated strength value, we can return messages

		//if value is less than 2
		if (strength < 2) {
			$('#div_password')
				.removeClass('has-success')
				.removeClass('has-warning')
				.addClass('has-error');
			return 'Password weak';
		} else if (strength == 2) {
			$('#div_password')
				.removeClass('has-error')
				.removeClass('has-success')
				.addClass('has-warning');
			return 'Good';
		} else {
			$('#div_password')
				.removeClass('has-error')
				.removeClass('has-warning')
				.addClass('has-success');
			return 'Strong';
		}
	}

	// confirm password
	$('#register_confirm_password').keyup(function() {
		const confirmPasswordInput = $(this);
		const confirmPassword = confirmPasswordInput.val();
		const password = $('#register_password').val();
		if (password && confirmPassword !== password) {
			$('#div_confirm_password')
				.removeClass('has-success')
				.addClass('has-error');
			$('#confirmPasswordHelpBlock').html('Passwords do not match');
		} else {
			$('#div_confirm_password')
				.removeClass('has-error')
				.addClass('has-success');
			$('#confirmPasswordHelpBlock').addClass('hikaya-hide');
		}
	});

	// Additional helper methods
	function isValidEmail(email) {
		var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
		return regex.test(email);
	}
});
