Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#add_stakeholder_modal',
	data: {
        name: '',
        stakeholderType: Number,
        sectors: [],
        stakeholder_label: '',
        stakeholderTypesList: [],
        sectorsList:[],
		showModal: false,
		isEdit: false,
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/stakeholder_dependant_data')
			.then(response => {
				if (response.data) {
                    this.stakeholder_label = response.data.stakeholder_label;
                    this.modalHeader = `Add ${this.stakeholder_label}`;
                    this.stakeholderTypesList = response.data.stakeholder_types;
                    this.sectorsList = response.data.sectors;
				}
			})
			.catch(e => {
				toastr.error( 'There was a problem loading stakeholders from the database');
			});
	},
	methods: {
        /**
         * open or close the stakeholder form modal
         * @param { object } item - stakeholder item
         */
		toggleModal: function(item = null) {
            this.showModal = !this.showModal;
            this.isEdit = false;
            this.modalHeader = `Add ${this.stakeholder_label}`;
            this.name = null;
            this.stakeholderType = null;
            this.sectors = [];
		},

        /**
         * process form data
         * @param { boolean } saveNew - true to keep the modal open for additional posts
         */
		processForm: function(saveNew = false) {
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
         * create new stakeholder
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/workflow/stakeholder/add`,
					{
                        stakeholder_name: this.name,
                        stakeholder_type: this.stakeholderType,
                        sectors: this.sectors
					}
                );
				if (response) {
                    toastr.success(`${this.stakeholder_label} successfully saved`);
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
                    this.name = '';
                    this.stakeholderType = '';
                    this.sectors = [];
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
         * Check if stakeholder form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
