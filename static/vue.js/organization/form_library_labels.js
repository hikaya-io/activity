Vue.use(VeeValidate);

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#formLibraryLabelsForm',
	data: {
        organization: null,
        individual_label: '',
		training_label: '',
        distribution_label: null,
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/organization/1/?user_org=1')
			.then(response => {
				if (response.data) {
					this.organization = response.data[0];
                    this.individual_label = this.organization.individual_label;
                    this.training_label = this.organization.training_label;
                    this.distribution_label = this.organization.distribution_label;
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading form library labels from the database!');
				this.organization = null;
			});
	},
	methods: {

        /**
         * edit form library labels
         */
		updateFormLibraryLabels() {
			try {
				const response = this.makeRequest(
					'PUT',
					`/workflow/organization/${this.organization.id}`,
					{
						individual_label: this.individual_label,
						training_label: this.training_label,
						distribution_label: this.distribution_label,
                    }
				);
				if (response) {
					toastr.success('Form library labels were successfully updated');
					this.organization = {
						individual_label: this.individual_label,
						training_label: this.training_label,
						distribution_label: this.distribution_label,
					}
				}
			} catch (e) {
				toastr.error('There was a problem updating your data');
			}
		},

		/**
         * Cancel edit form library labels
         */
		cancelUpdate() {
			this.individual_label = this.organization.individual_label;
			this.training_label = this.organization.training_label;
			this.distribution_label = this.organization.distribution_label;
		},

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
	},

	computed: {
        /**
         * Check if organization form is valid
         */
		// isFormValid() {
		// 	return this.name;
		// },
	},
});
