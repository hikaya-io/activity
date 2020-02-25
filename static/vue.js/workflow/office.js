Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#office',
	data: {
		showModal: false,
		showDeleteModal: false,
        offices: [],
        adminLevels: [],
        name: '',
        code: '',
		isEdit: false,
		currentOffice: null,
        itemToDelete: null,
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/office/')
			.then(response => {
				if (response.data) {
                    this.offices = response.data.sort((a, b) => b.id - a.id);
                    // this.adminLevels = response.data.adminLevels;
                    this.modalHeader = 'Add Office'; 
					$(document).ready(() => {
						$('#officesTable').DataTable({
                            pageLength: 5,
                            lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading offices from the database');
				this.offices = [];
			});
	},
	methods: {
        /**
         * open or close the fund code form modal
         * @param { object } item - fund code item
         */
		toggleModal: function(item = null) {
            this.showModal = !this.showModal;
			if (item) {
				this.isEdit = true;
				this.modalHeader = `Edit ${item.name}`;
				this.currentOffice = item;
                this.name = item.name;
                this.code = item.code;
			}
		},

        /**
         * open or close the fund code delete modal
         * @param { object } data - fund code item
         */
		toggleDeleteModal: function(data) {
			this.showDeleteModal = !this.showDeleteModal;
			this.modalHeader = 'Confirm delete';
			this.itemToDelete = data;
        },

        /**
         * process form data
         * @param { boolean } saveNew - true to keep the modal open for additional posts
         */
		processForm: function(saveNew = false) {
			this.$validator.validateAll().then(result => {
				if (result) {
					if (this.currentOffice && this.currentOffice.id) {
						this.updateFundCode();
					} else {
						if (saveNew) {
							this.postData(saveNew);
						} else {
							this.postData();
						}
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
					`/workflow/office/`,
					{
                        name: this.name,
                        code: this.code
					}
                );
				if (response) {
                    toastr.success('Fund Code successfuly saved');
					this.offices.unshift(response.data);
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
                    this.name = '';
                    this.code = '';
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data!!');
			}
		},

        /**
         * edit Fund Code item
         */
		async updateFundCode() {
			try {
				const response = await this.makeRequest(
					'PUT',
					`/workflow/office/${this.currentOffice.id}`,
					{ 
                        name: this.name, 
                        code: this.code,
                    }
				);
				if (response) {
					toastr.success('Offices was successfuly updated');
					const existingOffices = this.offices.filter(item => {
						return item.id != this.currentOffice.id;
					});
					this.offices = existingOffices;
					this.offices.unshift(response.data);
					this.isEdit = false;
                    this.name = null;
                    this.code = null;
                    this.currentOffice = null;
					this.modalHeader = 'Add Office';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data');
			}
		},

        /**
         * delete fund code
         * @param { number } id - id of the fund code to be deleted
         */
		async deleteOffice(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/workflow/office/${id}`
				);
				if (response.status === 204) {
					toastr.success('Office was successfuly deleted');
					this.offices = this.offices.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
				} else {
					toastr.error('There was a problem deleting office');
				}
			} catch (error) {
				toastr.error('There was a server error!!');
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
         * Check if fund code form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
