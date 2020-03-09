Vue.component('paginate', VuejsPaginate)

const beneficiariesComponent = Vue.component('beneficiaries-table', {
  template: '#participants-table-template',
});

$(document).ready(() => {
  const table = $('#trainingTable').DataTable();

  function format(trainingId, programId) {
    let div = $(`<div id="training-${trainingId}-beneficiaries"></div>`)
    $.ajax({
      url: `/formlibrary/training_participants/${trainingId}`,
      type: 'GET',
      success: function (result) {
        new beneficiariesComponent({
          delimiters: ['[[', ']]'],
          data: {
            participants: result['results'],
            perPage: 30,
            totalPages: 0,
            currentPage: 1
          },
          created() {
            this.setPageCount(result)
          },
          methods: {
            makeRequest(method, url, data = null) {
              axios.defaults.xsrfHeaderName = 'X-CSRFToken';
              axios.defaults.xsrfCookieName = 'csrftoken';
              return axios({method, url, data});
            },
            paginationHandler(page) {
              if (page !== this.currentPage) {
                this.fetchData(page)
              }
            },
            setPageCount(results) {
              this.totalPages = Math.ceil(results.count / this.perPage)
            },
            async fetchData(page) {
              try {
                const result = this.makeRequest(
                  'GET',
                  `/formlibrary/training_participants/${trainingId}?page=${page}&per_page=${this.perPage}`
                );
                this.participants = result['results']
                this.setPageCount(result)
              } catch (e) {
                console.log(e)
                toastr.error('There was a problem loading the participants.');
              }
            }
          }
        }).$mount(`#training-${trainingId}-beneficiaries`);
      },
      error: (error) => {
        console.log(error)
        toastr.error('There was a problem loading the participants.');
      }
    });
    return div
  }

  $('#trainingTable tbody').on('click', 'td.details-control', function () {
    let trainingId = $(this).data('indicator-id');
    let programId = $(this).data('program-id');
    let tr = $(this).closest('tr');
    let row = table.row(tr);
    if (row.child.isShown()) {
      row.child.hide();
      tr.removeClass('shown');
    } else {
      row.child(format(trainingId, programId)).show();
      tr.addClass('shown');
    }
  });
});
