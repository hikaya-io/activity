Vue.use(VeeValidate);
Vue.component('modal', {
  template: '#modal-template'
});

new Vue({
    delimiters: ['[[', ']]'],
	el: '#indicators_list',
	data: {
        overall_target: '',
        indicator_id: '',
        baseline: '',
        rationale: '',
        target_frequency: '',
        number_of_target_periods: '1',
        target_frequency_start: '',
        showModal: false,
        showDeleteModal: false,
        modalHeader: "",
        isEdit: false,
        show: false,
        showTable: false,
        disabledClass: false,
        targets: [],
        level_1_label: '',
        sum: 0,
        target_value: {},
        target_period_data: [],
        frequencies: null,
        indicatorList: []       
    },
    beforeMount: function() {
		this.makeRequest('GET', '/indicators/periodic_target/')
			.then(response => {
				response.data.forEach(target => {
                    this.target_period_data.push(target)
                })                
			})
			.catch(e => {
				toastr.error('There was a problem loading targets from the database');
            });
            
        this.makeRequest('GET', '/indicators/indicator_data')
            .then(response => {
                console.log(response)
                if(response.data){
                    this.level_1_label = response.data.level_1_label
                    this.frequencies = [{"id": "1", "text":`Life of ${this.level_1_label}`},
                                        {"id": "3", "text":"Every Year"},
                                        {"id": "4", "text":"Every Six Months"},
                                        {"id": "5", "text":"Every Four Months"},
                                        {"id": "6", "text":"Every Three Months"},
                                        {"id": "7", "text":"Every Month"},
                                        {"id": "8", "text":"Every Week"},
                                        {"id": "9", "text":"Every Two Weeks"}]

                    this.indicatorList = response.data.indicators

                }
            })
            .catch(e => {
				toastr.error('There was a problem loading Indicators from the database');
            });
	},
    methods: {
        makeRequest(method, url, data = null) {
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';
            axios.defaults.xsrfCookieName = 'csrftoken';
            return axios({method, url, data});
        },

        updateSum: function(){
            this.sum = 0
            for (var key in this.target_value) {
                if (this.target_value.hasOwnProperty(key)) {
                    this.sum += parseInt(this.target_value[key]) 
                }
            }
            
        },

        addPeriodTargets: function() {
            if (this.number_of_target_periods < 1) {
                return;
              }

            const periodStarts = moment(this.target_frequency_start).startOf("month");


            this.frequencies.forEach(frequency => {
                if (frequency.id === this.target_frequency){
                    switch (frequency.id) {
                        case "3":
                          this.generateYearlyTargets(periodStarts);
                          break;
                        case "4":
                          this.generateSemiAnnualTargets(periodStarts);
                          break;
                        case "5":
                          this.generateTriAnnualTargets(periodStarts);
                          break;
                        case "6":
                          this.generateQuarterlyTargets(periodStarts);
                          break;
                        case "7":
                          this.generateMonthlyTargets(periodStarts);
                          break;
                        case "8":
                          this.generateWeeklyTargets(periodStarts);
                          break;
                        case "9":
                          this.generateBiWeeklyTargets(periodStarts);
                          break;
                        default:
                          break;
                    }

                }
            })

            this.showTable = true
            this.disabledClass = true

            
        },

        removeTargetPeriods: function(){
            this.targets= [],
            this.target_value= {}
            this.sum= 0
            this.show=false
            this.showTable = false
            this.disabledClass = false
            this.target_frequency_start= ''

        },

        showFields: function(){
            this.show = true

            if (this.target_frequency == "1"){
                this.generateLOPTargets();
            }
        },

        generateLOPTargets: function(){
            this.showTable = true
            this.disabledClass = true
            const period = `Life of ${this.level_1_label}`
            const pk = 1
            
            this.indicatorList.forEach(indicator => {
                if (indicator.id == this.indicator_id){
                    const program = indicator.program[0]
                    const start_date = moment(program.start_date).format("MMM DD, YYYY");
                    const end_date = moment(program.end_date).format("MMM DD, YYYY");
                    this.target_frequency_start = moment(program.start_date).format("YYYY-MM");
                    this.targets = [...this.targets, { pk, start_date, end_date, period}];
                }
            })

        },

        generateWeeklyTargets: function(periodStart){
            for (let i = 1; i <= this.number_of_target_periods; i++) {
                const period = `Week ${i}`
                const pk = `${i}`
                let periodEnds = moment(periodStart)
                let start_date = moment(periodStart)
                            .startOf("day")
                            .format("MMM DD, YYYY");
                let end_date = moment(periodEnds)
                            .add(7, "days")
                            .endOf("day")
                            .format("MMM DD, YYYY");

                this.targets = [...this.targets, { pk, start_date, end_date, period}];

                periodStart = moment(periodEnds).add(8, "days");
            } 

        },

        generateBiWeeklyTargets: function(periodStart){
            for (let i = 1; i <= this.number_of_target_periods; i++) {
                const period = `Weeks ${i}`
                const pk = `${i}`
                let periodEnds = moment(periodStart)
                let start_date = moment(periodStart)
                            .startOf("day")
                            .format("MMM DD, YYYY");
                let end_date = moment(periodEnds)
                            .add(14 ,"days")
                            .endOf("day")
                            .format("MMM DD, YYYY");

                this.targets = [...this.targets, { pk, start_date, end_date, period}];

                periodStart = moment(periodEnds).add(15, "days");
            } 

        },

        generateYearlyTargets: function(periodStart){
            for (let i = 1; i <= this.number_of_target_periods; i++) {
                const period = `Year ${i}`
                const pk = `${i}`
                let periodEnds = moment(periodStart);
                let start_date = moment(periodStart)
                            .startOf("month")
                            .format("MMM DD, YYYY");
                let end_date = moment(periodEnds)
                            .add(11, "months")
                            .endOf("month")
                            .format("MMM DD, YYYY");

                this.targets = [...this.targets, { pk, start_date, end_date, period}];

                periodStart = moment(periodEnds).add(12, "months");
            }

        },

        generateSemiAnnualTargets: function(periodStart){
            for (let i = 1; i <= this.number_of_target_periods; i++) {
                const period = `SemiAnnual ${i}`
                const pk = `${i}`
                let periodEnds = moment(periodStart);
                let start_date = moment(periodStart)
                            .startOf("month")
                            .format("MMM DD, YYYY");
                let end_date = moment(periodEnds)
                            .add(5, "months")
                            .endOf("month")
                            .format("MMM DD, YYYY");

                this.targets = [...this.targets, { pk, start_date, end_date, period}];

                periodStart = moment(periodEnds).add(6, "months");
            }

        },

        generateTriAnnualTargets: function(periodStart){
            for (let i = 1; i <= this.number_of_target_periods; i++) {
                const period = `Triannual ${i}`
                const pk = `${i}`
                let periodEnds = moment(periodStart);
                let start_date = moment(periodStart)
                            .startOf("month")
                            .format("MMM DD, YYYY");
                let end_date = moment(periodEnds)
                            .add(3, "months")
                            .endOf("month")
                            .format("MMM DD, YYYY");


                this.targets = [...this.targets, { pk, start_date, end_date, period}];

                periodStart = moment(periodEnds).add(4, "months");
            }

        },

        generateQuarterlyTargets: function(periodStart){
            for (let i = 1; i <= this.number_of_target_periods; i++) {
                const period = `Quarter ${i}`
                const pk = `${i}`
                let periodEnds = moment(periodStart)
                let start_date = moment(periodStart)
                            .startOf("month")
                            .format("MMM DD, YYYY");
                let end_date = moment(periodEnds)
                            .add(2, "months")
                            .endOf("month")
                            .format("MMM DD, YYYY");


                this.targets = [...this.targets, { pk, start_date, end_date, period}];

                periodStart = moment(periodEnds).add(3, "months");
            }
        },

        generateMonthlyTargets: function(periodStart){
            for (let i = 1; i <= this.number_of_target_periods; i++) {
                const period = `Month ${i}`
                const pk = `${i}`
                let periodEnds = moment(periodStart)
                let start_date = moment(periodStart)
                            .startOf("month")
                            .format("MMM DD, YYYY");
                let end_date = moment(periodEnds)
                            .add("months")
                            .endOf("month")
                            .format("MMM DD, YYYY");

                this.targets = [...this.targets, { pk, start_date, end_date, period}];

                periodStart = moment(periodEnds).add(1, "months");
            } 
        },

        toggleTargetModal: function(indicator_id) {
            this.indicator_id = indicator_id
            this.overall_target = ''
            this.baseline= 0
            this.rationale= ''
            this.target_frequency= ''
            this.number_of_target_periods= '1'
            this.target_frequency_start= ''
            this.targets= [],
            this.target_value= {}
            this.sum= 0
            this.show=false
            this.showTable = false
            this.disabledClass = false
            this.isEdit = false
            this.modalHeader = "Add Target Periods"

            this.target_period_data.forEach(target =>{
                console.log(target)
                if(target.indicator.id == this.indicator_id){
                    console.log("gere")
                    this.isEdit = true
                    this.overall_target = target.indicator.lop_target
                    this.sum = target.indicator.lop_target
                    this.baseline= target.indicator.baseline
                    this.rationale= target.indicator.rationale_for_target
                    const pk = target.id
                    const start_date = target.start_date
                    const end_date = target.end_date
                    const period = target.period
                    const target_value = target.target
                    this.targets = [...this.targets, {pk, start_date, end_date, period, target_value}]
                    
                }
            })
            if(this.isEdit){
                this.targets.reverse()
                this.modalHeader = 'Edit Target Periods'
                this.targets.forEach(target => {
                    this.target_value[target.pk] = target.target_value
                })
                this.showTable = true
                this.show= true 
                this.disabledClass = true
                this.number_of_target_periods = this.targets.length
                this.target_frequency_start = moment(this.targets[0].start_date).format("YYYY-MM")
                if (this.targets[0].period.includes('Year')){
                    this.target_frequency = "3"
                }else if(this.targets[0].period.includes('Semi')){
                    this.target_frequency = "4"
                }else if(this.targets[0].period.includes('Tri')){
                    this.target_frequency = "5"
                }else if(this.targets[0].period.includes('Month')){
                    this.target_frequency = "7"
                }else if(this.targets[0].period.includes('Quarter')){
                    this.target_frequency = "6"
                }else if(this.targets[0].period.includes('Weeks')){
                    this.target_frequency = "9"
                }else if(this.targets[0].period.includes('Week')){
                    this.target_frequency = "8"
                }else if(this.targets[0].period.includes('life')){
                    this.target_frequency = "1"
                }

                
            }
   
            this.showModal = !this.showModal

        },
        toggleDeleteModal: function () {
            this.showDeleteModal = !this.showDeleteModal;
            this.modalHeader = 'Confirm delete';
          },

        processForm: function() {
            this.$validator.validateAll().then(target => {
                if (target) {
                    if (this.targets.length > 0){
                        if (parseInt(this.sum) === parseInt(this.overall_target)){
                            if(this.isEdit){
                                this.updateTargets()
                            }else{
                                this.postTarget()
                            }
                        }else{
                            toastr.error('The sum of target values must be equal to overall target');
                        }
                    }else{
                        toastr.error('Please add period targets');
                    }
                }
            });
        },

        async postTarget() {
            for (var key in this.target_value) {
                if (this.target_value.hasOwnProperty(key)) {
                    this.targets.forEach((target =>{
                        if (parseInt(key) === parseInt(target.pk)){
                            target["target"] = this.target_value[key]
                        }
                    }))
                     
                }
            }
            
            const id = this.indicator_id
            this.targets = this.targets.map(function (obj) {
                console.log(obj)
                obj['indicator_id'] = obj['id'];
                obj['start_date'] = moment(obj['start_date']).format("YYYY-MM-DD")
                obj['end_date'] = moment(obj['end_date']).format("YYYY-MM-DD")
                delete obj['id'];
                obj['indicator_id'] = id
                return obj;
            });
            const data = {
                indicator_id : id,
                indicator_LOP: this.overall_target,
                indicator_baseline: this.baseline,
                rationale : this.rationale,
                periodic_targets: this.targets
            }

            console.log(data)
            try {
                const response = await this.makeRequest(
                    'POST',
                    `/indicators/periodic_target/`,
                    {data}
                  );

                if (response){
                    this.toggleTargetModal();
                    this.target_period_data = []
                    response.data.data.forEach(target => {
                        this.target_period_data.push(target)
                    })
                    toastr.success('Target periods were saved successfully');
                    this.$validator.reset();
                }
            } catch (error) {
                toastr.error('There was a problems saving your data.');
            }

        },

        async updateTargets(){
            for (var key in this.target_value) {
                if (this.target_value.hasOwnProperty(key)) {
                    this.targets.forEach((target =>{
                        if (parseInt(key) === parseInt(target.pk)){
                            target["target"] = this.target_value[key]
                        }
                    }))
                     
                }
            }
            
            const id = this.indicator_id
            this.targets = this.targets.map(function (obj) {
                obj['indicator_id'] = obj['id'];
                obj['start_date'] = moment(obj['start_date']).format("YYYY-MM-DD")
                obj['end_date'] = moment(obj['end_date']).format("YYYY-MM-DD")
                delete obj['id'];
                obj['indicator_id'] = id
                return obj;
            });

            const data = {
                indicator_id : id,
                indicator_LOP: this.overall_target,
                indicator_baseline: this.baseline,
                rationale : this.rationale,
                periodic_targets: this.targets
            }

            try {
                const response = await this.makeRequest(
                    'PATCH',
                    `/indicators/periodic_target/`,
                    {data}
                  );

                if (response){
                    this.toggleTargetModal();
                    this.target_period_data = []
                    toastr.success('Target periods were updated successfully');
                    response.data.data.forEach(target => {
                        this.target_period_data.push(target)
                    })
                    this.$validator.reset();
                }
            } catch (error) {
                toastr.error('There was a problems updating your data.');
            }

        },


        async deleteTargets() {
            const id = this.indicator_id
            try {
              const response = await this.makeRequest(
                'DELETE',
                `/indicators/periodic_target/`,
                {id}
              );
              if (response) {
                this.target_period_data = []
                toastr.success('Target periods were successfully deleted.');
                response.data.data.forEach(target => {
                    this.target_period_data.push(target)
                })
                this.showDeleteModal = !this.showDeleteModal;
                this.toggleTargetModal();
              } else {
                this.modalHeader = 'Add Target Periods';
                toastr.error('There was a problem deleting the targets.');
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
});