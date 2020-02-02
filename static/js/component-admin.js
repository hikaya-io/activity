$(document).ready(() => {
  // show quick add modal if quick-modal to true
//   const url = new URL(window.location.href);
//   if (url.searchParams.get('quick-modal')) {
//     $('#addProfileTypesModal').modal('show');
//   }
});

var siteLabel = '';
function getSiteLabel (siteLabel) {
    siteLabel = siteLabel;
}

var saveProfileType = buttonId => {
  $(`#${buttonId}`).click(e => {
    e.preventDefault();
    const formValue = $('#addProfileTypesForm').serializeArray();
    const obj = {};
    formValue.forEach(item => {
      obj[item.name] = item.value;
    });

    $.ajax({
      url: '/workflow/profile_type/add',
      type: 'POST',
      data: obj,
      success: function(resp, status) {
        if (resp.success) {
          // notify success
          toastr.success(
            siteLabel + ' Type was added sucessfully',
          );
        } else {
          // Saving failed
          toastr.error(
            'The ' + siteLabel + ' Type was not added',
            'Failed',
          );
        }
        //close modal
        $('#addProfileTypesModal').modal('hide');
        // reset form
        $('#addProfileTypesModal').trigger('reset');

        const urlWithoutQueryString = window.location.href.split('?')[0];
        if (buttonId === 'saveProfileTypeAndNew') {
          window.location.replace(`${urlWithoutQueryString}?quick-modal=true`);
        } else {
          setTimeout(() => {
            window.location.replace(urlWithoutQueryString);
          }, 2000);
        }
      },
      error: function(xhr, status, error) {
        toastr.error(error, 'Failed');
      },
    });
  });
};

$(() => {
  saveProfileType('saveProfileTypeAndNew');
  saveProfileType('saveProfileType');
});
