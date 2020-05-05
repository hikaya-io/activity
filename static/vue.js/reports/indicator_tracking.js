Vue.use(VeeValidate);
Vue.component('v-select', VueSelect.VueSelect);

new Vue({
    delimiters: ['[[', ']]'],
    el: '#indicator_tracking_tables',
    data: {
        programList: [],
        reporting_periods: [],
        program_id: '',
        reporting_period_id: '',
        disabled_class: true,
        start_date: '',
        end_date:'',
    },

    beforeMount: function() {
        this.makeRequest('GET', '/workflow/level1_dependant_data')
            .then(response => {
                if (response.data) {
                    this.programList = response.data.programs.sort((a, b) => (a.name > b.name) ? 1 : -1);
            }
        })
        .catch(e => {
            toastr.error('There ws a problem loading programs from the database');
        });

    },
    methods: {
        makeRequest(method, url, data = null) {
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';
            axios.defaults.xsrfCookieName = 'csrftoken';
            return axios({method, url, data});
        },

        generatePeriods: function(start_date, end_date){
            const start = moment(start_date)
            const end = moment(end_date)
            const monthly = {"id":'1', "label":"Monthly"}
            const quaterly = {"id":'2', "label":"Quarterly"}
            const annually = {"id":'3', "label":"Annually"}
            this.reporting_periods = []

            const diff = end.diff(start, 'months', true)
            console.log(diff)

            if(Number(diff) >= 12){
                this.reporting_periods = [ monthly, quaterly, annually]

            }else if(Number(diff) < 12 && Number(diff) >= 6){
                this.reporting_periods = [ monthly, quaterly]
            }else if(Number(diff) < 6){
                this.reporting_periods = [ monthly]
            }

        },

        generateReport: function(){
            try {
				const response = this.makeRequest(
					'GET',
					`/reports/quaterly_report/${this.program_id}/${this.reporting_period_id}`
				);
				if (response) {
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving');
			}
        },

        processForm: function() {
			this.$validator.validateAll().then(res => {
				if (res) {
                    console.log('here')
					this.generateReport()
				}
			});
		},
        
    },

    watch: {
        program_id: function () {
          this.programList.forEach(program => {
            if (program.id === Number(this.program_id)) {
                this.start_date =  moment(program.start_date).format("YYYY-MM-DD")
                this.end_date = moment(program.end_date).format("YYYY-MM-DD")

                this.generatePeriods(this.start_date, this.end_date)

                this.disabled_class = false

            }
          })

        }
      }
  });