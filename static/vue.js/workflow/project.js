Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#add_project_modal',
	data: {
        name: '',
		program: Number,
		programsList: [],
		level_2_label: '',
		showModal: false,
		isEdit: false,
		modalHeader: '',
		saveNew: false,
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/project_dependant_data')
			.then(response => {
				if (response.data) {
					this.level_2_label = response.data.level_2_label;
					this.modalHeader = `Add ${this.level_2_label}`; 
					this.programsList = response.data.programs;
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading projects from the database!!');
			});
	},
	methods: {
        /**
         * open or close the fund code form modal
         * @param { object } item - fund code item
         */
		toggleModal: function(item = null) {
			this.showModal = !this.showModal;
		},

        /**
         * process form data
         * @param { boolean } saveNew - true to keep the modal open for additional posts
         */
		processForm: function(saveNew = false) {
			this.saveNew = saveNew;
			this.$validator.validateAll().then(result => {
				if (result) {
					if (saveNew) {
						this.postData(saveNew);
					} else {
						this.postData();
					}
				}
			});
		},

        /**
         * create new fund code
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {

			try {
				const response = await this.makeRequest(
					'POST',
					`/workflow/level2/add`,
					{
						project_name: this.name,
						program: this.program,
					}
                );
				if (response) {
					toastr.success(`${this.level_2_label} successfuly saved`);
					location.reload();
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.name = '';
					this.program = null;
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data!!');
			}
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
         * Check if project form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
