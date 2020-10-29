Vue.use(VeeValidate);
const modal = Vue.component('modal', {
  template: '#modal-template',
});

const detailComponent = Vue.component('individual-data-table', {
  template: '#individual-data-table-template',
});

$(document).ready(() => {
  const table = $('#individualsTable').DataTable();

  function format(householdId, ) {
    let div = $(`<div id="details-${householdId}"></div>`);
    $.ajax({
      url: `/individual/${householdId}`,
      type: 'GET',
      success: function (result) {
        new detailComponent({
          delimiters: ['[[', ']]'],
          data: {
            documentationList: JSON.parse(document.getElementById('documentation-data').textContent),
            collectedData: result,
            showModal: false,
            showDeleteModal: false,
            modalHeader: "Add Individual",
            level_1_label: '',
            individual_label: '',
            modalHeader: '',
            create_data: {
              first_name : '',
              last_name : '',
              date_of_birth : '',
              id_number : 0,
              primary_phone : '',
              sex : '',
              program: 0,
            },
            individualsList: [],
            trainingList:[],
            distributionsList:[],
            programsList:[],
            programs: [],
            showModal: false,
            isEdit: false,
            saveNew: false,
            showDeleteModal: false,
            itemToDelete: null,
          },
          methods: {
            makeRequest(method, url, data = null) {
              axios.defaults.xsrfHeaderName = 'X-CSRFToken';
              axios.defaults.xsrfCookieName = 'csrftoken';
              return axios({ method, url, data });
            },
            toggleResultModal: function (item = null) {
              this.showModal = !this.showModal;
              this.modalHeader = `Add Individual`;    
              this.create_data =  {
                first_name : '',
                last_name : '',
                date_of_birth : '',
                id_number : 0,
                primary_phone : '',
                sex : '',
                program: 0,
            };
              if(this.showModal) {
                let self = this;
                setTimeout(() => {
                  $("#dateCollected").datepicker({
                    dateFormat: "yy-mm-dd",
                    onSelect: function (dateText) {
                      self.date_collected = dateText;
                    }
                  })
                  if(item) {
                    $("#dateCollected").datepicker('setDate', item.date_collected);
                  } else {
                    $("#dateCollected").datepicker('setDate', "");
                  }
                }, 0)
              } else {
                $("#dateCollected").datepicker('hide').datepicker('destroy');
              }
            

              if (item) {
                this.isEdit = true;
                this.modalHeader = `Edit Result`;
                this.currentResult = item;
                this.date_collected = item.date_collected
                this.target = item.targeted
                this.actual = item.achieved
                this.documentation = item.evidence
                if (item.disaggregation_value.length > 0) {
                  this.show_disaggregations = true
                  item.disaggregation_value.forEach(disaggregation => {
                    this.disaggregations[disaggregation.disaggregation_label.id] = disaggregation.value
                  })

                }
              } else {
                this.isEdit = false;
              }
            },


            formatDate: function (date) {
              return moment(date, 'YYYY-MM-DDThh:mm:ssZ').format('YYYY-MM-DD');
            },

            validateDisaggregations: function () {
              let sum = 0
              this.validate_disaggregation = true

              if (Object.keys(this.disaggregations).length > 0) {
                this.collectedData.indicator.disaggregation.forEach(disagg => {
                  disagg.disaggregation_label.forEach(disagg_label => {
                    const entries = Object.entries(this.disaggregations)
                    for (const [id, value] of entries) {
                      if (parseInt(id) === disagg_label.id) {
                        sum += parseInt(value)
                      }
                    }
                  })
                  if (sum !== parseInt(this.actual)) {
                    toastr.error(`Total for ${disagg.disaggregation_type} does not match the actual value`);
                    this.validate_disaggregation = false
                  }
                  sum = 0
                })
              }
            },

            processForm: function (saveNew = false) {
              this.$validator.validateAll().then(result => {
                this.validateDisaggregations();
                if (result && this.validate_disaggregation) {
                  if (this.currentResult && this.currentResult.id) {
                    this.updateResult();
                  } else {
                    if (saveNew) {
                      this.postData(saveNew);
                    } else {
                      this.postData();
                    }
                  }
                }
              });
            },

            async postData(saveNew) {
              try {
                const response = await this.makeRequest(
                  'POST',
                  `/indicators/collecteddata/add`,
                  {
                    actual: this.actual,
                    target: this.target,
                    date_collected: this.date_collected,
                    period: this.period,
                    indicator: indicatorId,
                    documentation: this.documentation,
                    program: programId,
                    disaggregations: this.disaggregations
                  }
                );
                if (response) {
                  toastr.success('Result successfuly saved');
                  this.collectedData.periodictargets.forEach(periodictarget => {
                    if (periodictarget.id == response.data.collected_data.periodic_target) {
                      periodictarget.collecteddata_set.push(response.data.collected_data);
                    }
                  })
                  if (!saveNew) {
                    this.toggleResultModal();
                  }
                  // resetting the form
                  this.date_collected = '';
                  this.target = '';
                  this.actual = 0;
                  this.documentation = '';
                  this.show_disaggregations = false
                  this.disaggregations = {}
                  this.$validator.reset();
                }
                ;
              } catch (error) {
                toastr.error('There was a problem saving your result');
              }
            },

            async updateResult() {
              try {
                const response = await this.makeRequest(
                  'PUT',
                  `/indicators/collected_data/edit/${this.currentResult.id}`,
                  {
                    actual: this.actual,
                    target: this.target,
                    date_collected: this.date_collected,
                    period: this.period,
                    documentation: this.documentation,
                    disaggregations: this.disaggregations
                  }
                );
                if (response) {
                  toastr.success('Result was successfuly updated');
                  this.collectedData.periodictargets.forEach(periodictarget => {
                    if (periodictarget.id == response.data.collected_data.periodic_target) {
                      periodictarget.collecteddata_set = periodictarget.collecteddata_set.filter(item => +item.id !== +this.currentResult.id)
                      periodictarget.collecteddata_set.unshift(response.data.collected_data);
                    }
                  })
                  this.isEdit = false;
                  this.currentResult = null;
                  this.modalHeader = 'Add Result';
                  this.toggleResultModal();
                }
              } catch (e) {
                toastr.error('There was a problem updating your results');
              }
            },

            async deleteResult(itemToDelete) {
              try {
                const response = await this.makeRequest(
                  'DELETE',
                  `/indicators/collected_data/delete/${itemToDelete.id}`
                );
                if (response.data.success) {
                  toastr.success('Result was successfully deleted');
                  this.collectedData.periodictargets.forEach(periodictarget => {
                    if (periodictarget.id == itemToDelete.periodic_target) {
                      periodictarget.collecteddata_set = periodictarget.collecteddata_set.filter(item => +item.id !== +itemToDelete.id)
                    }
                  })
                  this.showDeleteModal = !this.showDeleteModal;
                  this.modalHeader = 'Add Result';
                } else {
                  this.modalHeader = 'Add Result';
                  toastr.error('There was a problem deleting the result');
                }
              } catch (error) {
                toastr.error('There was a server error');
              }
            },


          },

          computed: {
            /**
             * Check if frequency form is valid
             */
            isFormValid() {
              return true;
            },
          },

          watch: {
            period: function () {
              this.targets.forEach(tag => {
                if (tag.id === Number(this.period)) {
                  this.target = tag.target
                }
              })

            }
          }
        }).$mount(`#details-${indicatorId}`);
      },
      error: (error) => {
        toastr.error('There was a problem loading the collected data.');
      }
    });
    return div
  }
});
