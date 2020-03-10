Vue.use(VeeValidate);
Vue.component('modal', {
  template: '#modal-template'
});

new Vue({
    delimiters: ['[[', ']]'],
	el: '#',
	data: {
        overall_target: '',
        baseline: '',
        rationale: '',
        target_frequency: '',
        target_periods:'',
        showModal: false,
        showDeleteModal: false,
        modalHeader: "Add Target Period",
        isEdit: '',
        currentPeriod: null,
        itemToDelete: null,
    },
    beforeMount: function(){
        async getTargetFrequency(item = null) {

        }
    },
    
    methods: {
        makeRequest(method, url, data = null) {
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';
            axios.defaults.xsrfCookieName = 'csrftoken';
            return axios({method, url, data});
        },

        generateYearlyTargets: function(){

        },

        generateSemiAnnualTargets: function(){

        },

        generateTriAnnualTargets: function(){

        },

        generateQuarterlyTargets: function(){

        },

        generateMonthlyTargets: function(){
            
        },


        toggleModal: function(item = null) {

            
        },

        processForm: function(saveNew = false) {

        },

        async postTarget(saveNew) {

        },

        async updateTarget() {

        },

        async deleteObjective(id) {

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