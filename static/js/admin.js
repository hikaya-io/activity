$(document).ready(function() {
  $('#userTable').DataTable();

  $('#id_user_email_list').select2({
    theme: 'bootstrap',
    tags: true,
  });
  $('#id_organization').select2({
    theme: 'bootstrap',
  });

  // Reset form
  $('#configForm').trigger('reset');
  let invalidInputs = [];
  //   validateConfigForm();

  // required fields
  $('#workflowlevel1').on('input focus keyup', function() {
    const wfl1 = $(this);
    if (wfl1.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'level_1_label');
      $('#div_workflowlevel1_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#wfl1HelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('level_1_label') === -1
        ? invalidInputs.push('level_1_label')
        : '';
      $('#div_workflowlevel1_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#wfl1HelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#workflowlevel2').on('input focus keyup', function() {
    const wfl2 = $(this);
    if (wfl2.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'level_2_label');
      $('#div_workflowlevel2_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#wfl2HelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('level_2_label') === -1
        ? invalidInputs.push('level_2_label')
        : '';
      $('#div_workflowlevel2_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#wfl2HelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#workflowlevel3').on('input focus keyup', function() {
    const wfl3 = $(this);
    if (wfl3.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'level_3_label');
      $('#div_workflowlevel3_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#wfl3HelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('level_3_label') === -1
        ? invalidInputs.push('level_3_label')
        : '';
      $('#div_workflowlevel3_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#wfl3HelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#workflowlevel4').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'level_4_label');
      $('#div_workflowlevel4_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#wfl4HelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('level_4_label') === -1
        ? invalidInputs.push('level_4_label')
        : '';
      $('#div_workflowlevel4_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#wfl4HelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#indicator').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'indicator_label');
      $('#div_indicator_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#indicatorHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('indicator_label') === -1
        ? invalidInputs.push('indicator_label')
        : '';
      $('#div_indicator_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#indicatorHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#site').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'site_label');
      $('#div_site_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#siteHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('site_label') === -1
        ? invalidInputs.push('site_label')
        : '';
      $('#div_site_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#siteHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#stakeholder').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(
        item => item !== 'stakeholder_label',
      );
      $('#div_stakeholder_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#stakeholderHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('stakeholder_label') === -1
        ? invalidInputs.push('stakeholder_label')
        : '';
      $('#div_stakeholder_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#stakeholderHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#form').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'form_label');
      $('#div_form_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#formHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('form_label') === -1
        ? invalidInputs.push('form_label')
        : '';
      $('#div_form_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#formHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#default_currency').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'default_currency');
      $('#div_currency_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#currencyHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('default_currency') === -1
        ? invalidInputs.push('default_currency')
        : '';
      $('#div_currency_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#currencyHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#date_format').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'date_format');
      $('#div_date_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#dateHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('date_format') === -1
        ? invalidInputs.push('date_format')
        : '';
      $('#div_date_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#dateHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#default_language').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'default_language');
      $('#div_language_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#languageHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('default_language') === -1
        ? invalidInputs.push('default_language')
        : '';
      $('#div_language_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#languageHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#theme_color').on('input focus keyup', function() {
    const wfl4 = $(this);
    if (wfl4.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'theme_color');
      $('#div_theme_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#themeHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('theme_color') === -1
        ? invalidInputs.push('theme_color')
        : '';
      $('#div_theme_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#themeHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#individual').on('input focus keyup', function() {
    const individual = $(this);
    if (individual.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'individual_label');
      $('#div_individual_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#individualHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('individual_label') === -1
        ? invalidInputs.push('individual_label')
        : '';
      $('#div_individual_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#individualHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#distribution').on('input focus keyup', function() {
    const distribution = $(this);
    if (distribution.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'distribution_label');
      $('#div_distribution_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#distributionHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('distribution_label') === -1
        ? invalidInputs.push('distribution_label')
        : '';
      $('#div_distribution_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#distributionHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });

  $('#training').on('input focus keyup', function() {
    const training = $(this);
    if (training.val()) {
      invalidInputs = invalidInputs.filter(item => item !== 'training_label');
      $('#div_training_name')
        .removeClass('has-error')
        .addClass('has-success');
      $('#trainingHelpBlock')
        .removeClass('hikaya-show')
        .addClass('hikaya-hide');
    } else {
      invalidInputs.indexOf('training_label') === -1
        ? invalidInputs.push('training_label')
        : '';
      $('#div_training_name')
        .removeClass('has-success')
        .addClass('has-error');
      $('#trainingHelpBlock')
        .removeClass('hikaya-hide')
        .addClass('hikaya-show');
    }
    validateConfigForm();
  });


  /*
   * Enable/Disable submit button
   */
  function validateConfigForm() {
    if (invalidInputs.length) {
      $('#config_submit_btn').attr('disabled', 'disabled');
    } else {
      $('#config_submit_btn').removeAttr('disabled');
    }
  }
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
      toastr.success('Your update has been saved.', 'Succesfully Updated');
      setTimeout(() => {
        document.location.reload();
      }, 2000);
    },
    error: function(xhr, desc, error) {
      toastr.error(
        'An error occured during the operation',
        'An Error occurred',
      );
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
      toastr.error(
        `The email [${element}] is invalid`,
        'Invalid Email Address',
      );
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
      success: function(res) {
        if (res.user_exists) {
          toastr.error(
            `A user with this email address already belongs to organization: ${res.organization}`,
            'User Exists',
          );
          setTimeout(() => {
            window.location.reload();
          }, 3000);
        } else {
          toastr.success(
            `You have successfully invited ${data.user_email_list.length} user(s)`,
            'Invitation Successful',
          );
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        }
      },
      error: function(xhr, desc, error) {
        toastr.error('Could not invite user', 'An Error occurred');
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
