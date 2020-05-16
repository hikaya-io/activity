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
        report_data: null,
        report_start: null,
        report_end: null,
        row_header_data: ['No.', 'Indicator', 'Level', 'Unit of Measure', 'Baseline', 'Target', 'Actual', '% Met'],
        row_body_data: [],
        loading : false,
        no_data: true
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
            const start = moment(start_date).startOf("month")
            const end = moment(end_date).endOf("month")
            const monthly = {"id":'1', "label":"Monthly"}
            const quarterly = {"id":'2', "label":"Quarterly"}
            const annually = {"id":'3', "label":"Annually"}
            this.reporting_periods = []

            const diff = end.diff(start, 'months', true)

            if(Number(diff) > 11.9){
                this.reporting_periods = [ monthly, quarterly, annually]

            }else if(Number(diff) < 12 && Number(diff) >= 6){
                this.reporting_periods = [ monthly, quarterly]
            }else if(Number(diff) < 6){
                this.reporting_periods = [ monthly]
            }

        },


        processForm: function() {
			this.$validator.validateAll().then(res => {
				if (res) {
                    this.loading = true
                    this.no_data = false
                    this.report_data = null
                    this.row_header_data = ['No.', 'Indicator', 'Level', 'Unit of Measure', 'Baseline', 'Target', 'Actual', '% Met'],
                    this.row_body_data = []
					this.generateReport()
				}
			});
        },
        
        async generateReport(){
            try {
				const response = await this.makeRequest(
					'GET',
					`/reports/quarterly_report/${this.program_id}/${this.reporting_period_id}`
				);
				if (response) {
                    this.report_data = response.data.data
                    this.report_start = moment(this.report_data[0].indicator[0].program[0].start_date).format('MMMM DD, YYYY')
                    this.report_end = moment(this.report_data[0].indicator[0].program[0].end_date).format('MMMM DD, YYYY')

                    this.report_data[0].raw_data.forEach(data =>{
                        this.row_header_data.push('Target')
                        this.row_header_data.push('Actual')
                        this.row_header_data.push('% Met')
                    })

                    this.report_data.forEach(data =>{
                        let level_name = null

                        if (data.indicator[0].level.length > 0){
                            level_name = data.indicator[0].level[0].name
                        }
                        let raw_table_data = {
                        'number': data.indicator[0].number || "-",
                        'name': data.indicator[0].name,
                        'level': level_name || "-",
                        'unit_of_measure': data.indicator[0].unit_of_measure || "-",
                        'baseline': data.indicator[0].baseline,
                        'total_target': data.total_targeted,
                        'total_achieved': data.total_achieved,
                        'total_perct_met': data.total_perct_met,
                        'raw': []
                        }

                        data.raw_data.forEach(row => {
                            raw_table_data.raw.push(row.target || '-')
                            raw_table_data.raw.push(row.actual || '-')
                            raw_table_data.raw.push(row.perct_met)
                        })

                        this.row_body_data.push(raw_table_data)
                    })
                         
                    this.$validator.reset();
                    this.loading = false
				}
			} catch (error) {
				toastr.error('There was a problem generating report');
			}
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