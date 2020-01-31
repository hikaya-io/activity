$(document).ready(() => {
    $('#id_evidence').select2({
        theme: 'bootstrap'
    });
    $('#addCollectedDataModal').on('hidden.bs.modal', function(e){ 
        $(".target_period").html("");
        $('#addCollectedDataForm').trigger('reset');
    });
$('#id_date_collected').on('input', function () {
    const name = $(this);
    if (name.val()) {
        $('#div_date_collected')
            .removeClass('has-error')
            .addClass('has-success');
        $('#dateHelpBlock')
            .removeClass('hikaya-show')
            .addClass('hikaya-hide');
    } else {
        $('#div_date_collected')
            .removeClass('has-success')
            .addClass('has-error');
        }
    });
$('#id_actual').on('input', function () {
    const name = $(this);
    if (name.val()) {
        $('#div_actual_value')
            .removeClass('has-error')
            .addClass('has-success');
        $('#actualHelpBlock')
            .removeClass('hikaya-show')
            .addClass('hikaya-hide');
    } else {
        $('#div_actual_value')
            .removeClass('has-success')
            .addClass('has-error');
        }
    });
$('#id_periodic_target').on('change', function () {
    const name = $(this);
    if (name.val()) {
        $('#div_periodic_target')
            .removeClass('has-error')
            .addClass('has-success');
        $('#periodHelpBlock')
            .removeClass('hikaya-show')
            .addClass('hikaya-hide');
    } else {
        $('#div_periodic_target')
            .removeClass('has-success')
            .addClass('has-error');
        }
    });

// show quick add modal if quick-modal to true
const url = new URL(window.location.href);
if (url.searchParams.get('open-modal')) {
        $('#addCollectedDataModal').modal('show');
    }
})
$(document).on("click", ".collectdata", function () {
var indicatorId = $(this).data('indicator');
$(".target_period").select2({
    theme: 'bootstrap',
    placeholder: "Select Target Period",
    ajax: {
        url: '/indicators/get_target/'+ indicatorId + '/',
        dataType: 'json',
        type: 'GET',
        processResults: function (data) {
            var res = data.data.map(function (item) {
                    return {id: item.pk, text: item.period};
            });
            return {
            results: res
        };
    }
}
});
})
var saveCollectedData = buttonId => {
    $(`#${buttonId}`).click(e => {
        e.preventDefault();
        const formValue = $('#addCollectedDataForm').serializeArray();
        const data = {"periodic_target":''}

        var indicatorId = $('#id_periodic_target').attr('data-tag')
        var programId = $('#id_periodic_target').attr('data-tag2')
        formValue.forEach(item => {
            data[item.name] = item.value;
        });

        data['indicator'] = indicatorId
        data['program'] = programId
        if (data.date_collected=='' || data.actual == '' || data.periodic_target == '') {
            if(data.date_collected==''){    
                $('#div_date_collected')
                .removeClass('has-success')
                .addClass('has-error');
                $('#dateHelpBlock')
                .removeClass('hikaya-hide')
                .addClass('hikaya-show');
            }
            if(data.actual == ''){
                $('#div_actual_value')
                .removeClass('has-success')
                .addClass('has-error');
                $('#actualHelpBlock')
                .removeClass('hikaya-hide')
                .addClass('hikaya-show');
            }
            if(data.periodic_target == ''){
                $('#div_periodic_target')
                .removeClass('has-success')
                .addClass('has-error');
                $('#periodHelpBlock')
                .removeClass('hikaya-hide')
                .addClass('hikaya-show');}

            toastr.error('Fill in all required fields');
        } else {
            $.ajax({
                url: myURL,
                type: 'POST',
                data: data,
                success: function(resp, status) {
                    const urlWithoutQueryString = window.location.href.split('?')[0];
                    if (buttonId === 'addCollectedDataAndNew') {
                        // notify success
                        toastr.success('Collected Data was added sucessfully, You can now add another one');
                        $('#id_actual').val("");
                        $('#div_actual_value').removeClass('has-success')
                        $('#id_date_collected').val("");
                        $('#div_date_collected').removeClass('has-success')
                        $('#div_periodic_target').removeClass('has-success')
                    } else {
                         // notify success
                        toastr.success('Collected Data was added sucessfully');
                        //close modal
                        $('#addCollectedDataModal').modal('hide');
                        // reset form
                        $('#addCollectedDataForm').trigger('reset');
                        setTimeout(() => {
                            window.location.replace(urlWithoutQueryString);
                        }, 2000);
                    }
                },
                error: function(xhr, status, error) {
                    toastr.error(error, 'Failed');
                },
            });
            
        }            
    });
};

$(() => {
    saveCollectedData('addCollectedData');
    saveCollectedData('addCollectedDataAndNew');
});