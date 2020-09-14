Vue.use(VeeValidate);
Vue.component('ValidationProvider', VeeValidate.ValidationProvider);
Vue.component('v-select', VueSelect.VueSelect);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#household_list',
	data: {
		householdsList: [],
		household_label: '',
		individual_label: '',
		name: '',
		showModal: false,
		showDeleteModal: false,
		programsList: [],
		programs: [],
		street: '',
		city:'',
		country: '',
		postal_code: '',
		primary_phone: '',
		secondary_phone: '',
		email: '',
		isEdit: false,
		saveNew: false,

		
	},
	beforeMount: function() {
		this.makeRequest('GET', '/formlibrary/household_list_data')
			.then(response => {
				if (response.data) {
					this.householdsList = response.data.households.sort((a, b) => (a.name > b.name) ? 1 : -1);
					this.programsList = response.data.programs;
					this.household_label = response.data.household_label;
					this.individual_label = response.data.individual_label;
					this.modalHeader = `Add ${this.household_label}`; 

					$(document).ready(() => {
						$('#householdTable').DataTable({
                            pageLength: 10,
                            lengthMenu: [10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading households from the database');
			});
	},
	methods: {
        /**
         * open or close the fund code form modal
         * @param { object } item - fund code item
         */
		toggleModal: function(item = null) {
			this.showModal = !this.showModal;
			this.modalHeader = `Add ${this.household_label}`; 
			if (!item) {
				this.name = '';
				this.programs = [];
				this.street = '';
				this.city = '';
				this.country = '';
				this.postal_code = '';
				this.primary_phone = '';
				this.secondary_phone = '';
				this.email = '';
			}
		},

		/**
         * Format date
         * @param {string} date - date to be formatted
         */
        formatDate: function(date) {
            return date ? moment(date, 'YYYY-MM-DDThh:mm:ssZ').format('YYYY-MM-DD') : '';
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
					`/formlibrary/household/`,
					{
						name: this.name, 
						program: this.programs,
						street: this.street,
						city: this.city,
						country: this.country,
						postal_code: this.postal_code,
						primary_phone: this.primary_phone,
						secondary_phone: this.secondary_phone,
						email: this.email,
					}
                );
				if (response.data) {
					toastr.success(`${this.household_label} ${this.name} successfully saved`);
					this.householdsList.unshift(response.data);

					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.name = '';
					this.programs = [];
					this.street = '';
					this.city = '';
					this.country = '';
					this.postal_code = '';
					this.primary_phone = '';
					this.secondary_phone = '';
					this.email = '';
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data');
			}
		},


		/**
         * open or close the delete modal
         * @param { object } data - item to delete
         */
		toggleDeleteModal: function(data) {
			this.showDeleteModal = !this.showDeleteModal;
			this.modalHeader = 'Confirm delete';
			this.itemToDelete = data;
        },

		 /**
         * delete household
         * @param { number } id - id of the household to be deleted
         */
		async deleteHousehold(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/formlibrary/household/${id}`
				);
				if (response.status === 204) {
					toastr.success(`${this.household_label} was successfully deleted`);
					this.householdsList = this.householdsList.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
					this.modalHeader = `Add ${this.household_label}`; 
					this.itemToDelete = null;
				} else {
					toastr.error('There was a problem deleting household');
				}
			} catch (error) {
				toastr.error('There was a server error');
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

		disableDates(date, value) {
			if(date === 'start') {
				this.disabledDates.end = {
					to: new Date(value)
				}
			} else {
				this.disabledDates.start = {
					from: new Date(value)
				}
			}
		}
	},

	computed: {
        /**
         * Check if fund code form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
