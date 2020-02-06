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
    }, 
    beforeMount: function(){
        axios.get('/indicators/data_collection_frequency/list')
        .then(response => {
            if(response.data) {
                this.frequencies = response.data.sort((a, b) => b.id - a.id)
                console.log(this.frequenccies)
            }
            
        })
        .catch(e => {
            console.log(e)
        })
    },
    methods: {
        toggleModal: function() {
            this.showModal = !this.showModal
        },
        processForm: function() {

            this.$validator.validateAll().then((result) => {
                if (result) {
                    this.postData()
                }
            });
        },

        postData() {
            axios.defaults.xsrfHeaderName = "X-CSRFToken"
            axios.defaults.xsrfCookieName = 'csrftoken' 
            axios.post(
                `/indicators/data_collection_frequency/add`, 
                { frequency: this.frequency }
              )
                .then(response => {
                    if(response.data) {
                        this.frequencies.unshift(response.data);
                    }
                })
                .catch(e => {
                    console.log(e);
                })
        }
    },

    computed: {
        isFormValid () {
          return this.frequency;
        }
      }
  })