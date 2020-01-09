$(document).ready(function() {
	$('#org_name').on('input', function() {
		const orgNameInput = $(this);
		const orgName = orgNameInput.val();
		if (orgName && orgName.length > 2) {
			$('#div_org_name')
				.removeClass('has-error')
				.addClass('has-success');
			$('#orgFormSubmitBtn').removeAttr('disabled');
		} else {
			$('#div_org_name')
				.removeClass('has-success')
                .addClass('has-error');
			$('#orgFormSubmitBtn').attr('disabled', true);
            
		}
		$('#activity_url').val(`www.activity.hikaya.io/${cleanName(orgName)}`);
	});
});

function cleanName(name) {
	return name.replace(/ /g, '-').toLowerCase();
}
