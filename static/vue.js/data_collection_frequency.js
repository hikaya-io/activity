Vue.use(VeeValidate);
Vue.component('modal', {
    template: '#modal-template'
  })
  
  // start app
  new Vue({
    delimiters: ['[[', ']]'],
    el: '#data_collection_frequency',
    data: {
      showModal: false,
      frequency: '',
      frequencies: [],
      isEdit: false,
      currentFrequency: null,
      modalHeader:'Add Data Collection Frequency',
    }, 
    beforeMount: function(){
        this.makeRequest('GET', '/indicators/data_collection_frequency/list')
        .then(response => {
            if(response.data) {
                this.frequencies = response.data.sort((a, b) => b.id - a.id)
                $(document).ready(() => {
                    $('#dataCollectionFrequencyTable').DataTable({
                        "pageLength": 5
                    });
                });
            }
            
        })
        .catch(e => {
            console.log(e)
        })
    },
    methods: {
        toggleModal: function(item=null) {
            this.showModal = !this.showModal
            if(item) {
                this.isEdit = true;
                this.modalHeader = `Edit ${item.frequency}`
                this.currentFrequency = item;
                this.frequency = item.frequency;
            }
        },
        processForm: function(saveNew=false) {

            this.$validator.validateAll().then((result) => {
                if (result) {
                    if (this.currentFrequency && this.currentFrequency.id) {
                        this.updateFrequency()
                    } else {
                        if(saveNew) {
                            this.postData(saveNew);
                        } else {
                            this.postData();
                        }
                    }
                }
            });
        },

        postData(saveNew) {
            this.makeRequest(
                'POST',
                `/indicators/data_collection_frequency/add`, 
                { frequency: this.frequency }
              )
                .then(response => {
                    if(response.data) {
                        toastr.success('Frequency Successfuly Saved');
                        this.frequencies.unshift(response.data);
                        if(!saveNew) {
                            this.toggleModal();
                        }
                        // resetting the form
                        this.frequency = '';
                        this.$validator.reset();
                    }
                })
                .catch(e => {
                    toastr.error('There was a problem saving your data!!');
                })
        },

        updateFrequency() {
            this.makeRequest(
                'PUT',
                `/indicators/data_collection_frequency/edit/${this.currentFrequency.id}`, 
                { frequency: this.frequency }
              )
                .then(response => {
                    if(response.data) {
                        toastr.success('Frequency was successfuly Updated');
                        const newFrequencies = this.frequencies.filter(
                             item => { 
                                 return item.id != this.currentFrequency.id
                                }
                        );
                        this.frequencies = newFrequencies
                         this.frequencies.unshift(response.data)
                        this.isEdit = false;
                        this.frequency = null;
                        this.modalHeader = 'Add Data Collection Frequency';
                        this.toggleModal();
                    }
                })
                .catch(e => {
                    toastr.error('There was a problem updating your data!!');
                })

        },

        makeRequest(method, url, data=null) {
            axios.defaults.xsrfHeaderName = "X-CSRFToken"
            axios.defaults.xsrfCookieName = 'csrftoken' 
            return axios({method, url, data, })
        }

    },

    computed: {
        isFormValid () {
          return this.frequency;
          
        }
      }
  })