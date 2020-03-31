Vue.use(VeeValidate);
Vue.component('ValidationProvider', VeeValidate.ValidationProvider);
Vue.component('v-select', VueSelect.VueSelect);
Vue.component('modal', {
	template: '#modal-template',
	
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#level_1_list',
	components: {
		'v-select': VueSelect.VueSelect
	},
	data: {
		programsList: [],
		sectorsList: [],
        name: '',
		sectors: [],
		start_date: '',
		end_date: '',
		level_1_label: '',
		level_2_label: '',
		stakeholder_label: '',
		site_label: '',
		indicator_label: '',
		minDate: '',
		maxDate: '',
		showModal: false,
		isEdit: false,
		currentProgram: null,
		modalHeader: '',
		disabledDates: {
			start:{},
			end:{}
		},
		saveNew: false,
		showDeleteModal: false,
		itemToDelete: null,
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/level1_dependant_data')
			.then(response => {
				if (response.data) {
					this.programsList = response.data.programs.sort((a, b) => (a.name > b.name) ? 1 : -1);
					this.sectorsList = response.data.sectors;
					this.level_1_label = response.data.level_1_label;
					this.level_2_label = response.data.level_2_label;
					this.stakeholder_label = response.data.stakeholder_label;
					this.site_label = response.data.site_label;
					this.indicator_label = response.data.indicator_label;
					this.modalHeader = `Add ${this.level_1_label}`; 

					$(document).ready(() => {
						$('#level1Table').DataTable({
                            pageLength: 10,
                            lengthMenu: [10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading programs from the database');
			});
	},
	methods: {
        /**
         * open or close the fund code form modal
         * @param { object } item - fund code item
         */
		toggleModal: function(item = null) {
			this.showModal = !this.showModal;
			this.modalHeader = `Add ${this.level_1_label}`; 
			if (!item) {
				this.name = '';
				this.sectors = [];
				this.start_date = '';
				this.end_date = '';		
			}
		},

		/**
         * Format date
         * @param {string} date - date to be formatted
         */
        formatDate: function(date) {
            return date ? moment(date, 'YYYY-MM-DDThh:mm:ssZ').format('YYYY-MM-DD') : '';
        },

		customFormatter(date) {
			return moment(date).format('DD.MM.YYYY');
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
         * set minimum date
         */
		setMinDate: function() {
			this.minDate = this.start_date;
		},

		/**
         * set maximum date
         */
		setMaxDate: function() {
			this.maxDate = this.end_date;
		},

        /**
         * create new fund code
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/workflow/level1/`,
					{
						name: this.name,
						sector: this.sectors,
						start_date: this.start_date ? moment(this.start_date, 'YYYY-MM-DD').format('YYYY-MM-DDThh:mm:ssZ') : null,
                        end_date: this.end_date ? moment(this.end_date, 'YYYY-MM-DD').format('YYYY-MM-DDThh:mm:ssZ') : null
					}
                );
				if (response.data) {
					toastr.success(`${this.level_1_label} successfully saved`);
					this.programsList.unshift(response.data);

					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.name = '';
					this.sectors = [];
					this.start_date = '';
					this.end_date = '';
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data');
			}
		},

		/**
         * open or close the profile type delete modal
         * @param { object } data - profile type item
         */
		toggleDeleteModal: function(data) {
			this.showDeleteModal = !this.showDeleteModal;
			this.modalHeader = 'Confirm delete';
			this.itemToDelete = data;
        },

		 /**
         * delete program
         * @param { number } id - id of the program to be deleted
         */
		async deleteProgram(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/workflow/level1/${id}`
				);
				if (response.status === 204) {
					toastr.success(`${this.level_1_label} was successfully Deleted`);
					this.programsList = this.programsList.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
					this.modalHeader = `Add ${this.level_1_label}`; 
					this.itemToDelete = null;
				} else {
					toastr.error('There was a problem deleting program');
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
