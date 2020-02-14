Vue.use(VeeValidate); 
const results_form = Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#indicators_list',
	data: {
        showModal: false,
		programId: null,
		indicatorId: null,
        period: null,
        target: null,
        dateCollected: null,
        actual: null,
        evidence: null,
        periodicTargets: [],
		isEdit: false,
		currentFrequency: null,
		itemToDelete: null,
		modalHeader: 'Add result',
    },
    beforeMount: function() {
		console.log(this.showModal)
        
    },
	methods: {
        /**
         * make requests for CRUD operations using axios
         * @param { string } method - request method
         * @param { string } url  - request url
         * @param { string } data - request payload
         * @return { Promise } - axios respons ePromise
         */
		makeRequest(method, url, data = null) {
			axios.defaults.xsrfHeaderName = 'X-CSRFToken';
			axios.defaults.xsrfCookieName = 'csrftoken';
			return axios({ method, url, data });
        },
		
		async getTargets(){
			const response = await this.makeRequest(
				'GET',
				`/indicators/get_target/${this.indicatorId}/`,
				console.log(response)
			);
			
		},

        /**
         * open or close the frequency form modal
         * @param { object } item - frequency item
         */
		toggleResultModal: function(item = null) {
            this.showModal = !this.showModal;
            console.log(this.showModal)
			if (item) {
				this.isEdit = true;
				this.modalHeader = `Edit Result`;
			}
		},

        /**
         * process form data
         * @param { boolen } saveNew - true to keep the modal open for additional posts
         */
		processForm: function(saveNew = false) {
			this.$validator.validateAll().then(result => {
				if (result) {
					if (this.currentFrequency && this.currentFrequency.id) {
						this.updateResult();
					} else {
						if (saveNew) {
							this.addResult(saveNew);
						} else {
							this.addResult();
						}
					}
				}
			});
		},

        /**
         * Add a new result
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async addResult(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/indicators/data_collection_frequency/add`,
					{
						frequency: this.frequency,
					}
				);
				if (response) {
                    toastr.success('Frequency Successfuly Saved');
					this.frequencies.unshift(response.data);
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.frequency = '';
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data!!');
			}
		},

        /**
         * edit a result
         */
		async updateResult() {
			try {
				const response = await this.makeRequest(
					'PUT',
					`/indicators/data_collection_frequency/edit/${this.currentFrequency.id}`,
					{ frequency: this.frequency }
				);
				if (response) {
					toastr.success('Result was successfuly Updated');
					this.isEdit = false;
					this.modalHeader = 'Add result';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data!!');
			}
		},
	},

	computed: {
        /**
         * Check if results form is valid
         */
		isFormValid() {
			return this.data;
		},
	},
});
