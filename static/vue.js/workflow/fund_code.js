Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#fund_code',
	data: {
		showModal: false,
		showDeleteModal: false,
        fundCodes: [],
        stakeholders: [],
        name: '',
        stakeholder: '',
		isEdit: false,
		currentFundCode: null,
        itemToDelete: null,
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/fund_code/list')
			.then(response => {
				if (response.data) {
                    this.fundCodes = response.data.fund_codes.sort((a, b) => b.id - a.id);
                    this.stakeholders = response.data.stakeholders;
                    this.modalHeader = 'Add Fund Code'; 
					$(document).ready(() => {
						$('#fundCodesTable').DataTable({
                            pageLength: 5,
                            lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading fund codes from the database!!');
				this.fundCodes = [];
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
				this.currentFundCode = item;
                this.name = item.name;
                this.stakeholder = item.stakeholder;
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
         * Format date
         * @param {string} date - date to be formatted
         */
        formatDate: function(date) {
            return moment(date, 'YYYY-MM-DDThh:mm:ssZ').format('YYYY-MM-DD');
        },

        /**
         * process form data
         * @param { boolean } saveNew - true to keep the modal open for additional posts
         */
		processForm: function(saveNew = false) {
			this.$validator.validateAll().then(result => {
				if (result) {
					if (this.currentFundCode && this.currentFundCode.id) {
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
					`/workflow/fund_code/add`,
					{
                        name: this.name,
                        stakeholder: this.stakeholder
					}
                );
				if (response) {
                    toastr.success('Fund Code successfuly saved');
					this.fundCodes.unshift(response.data);
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
                    this.name = '';
                    this.stakeholder = '';
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
					`/workflow/fund_code/edit/${this.currentFundCode.id}`,
					{ 
                        name: this.name, 
                        stakeholder: this.stakeholder,
                    }
				);
				if (response) {
					toastr.success('Fund code was successfuly updated');
					const existingFundCodes = this.fundCodes.filter(item => {
						return item.id != this.currentFundCode.id;
					});
					this.fundCodes = existingFundCodes;
					this.fundCodes.unshift(response.data);
					this.isEdit = false;
                    this.name = null;
                    this.stakeholder = null;
					this.modalHeader = 'Add Fund Code';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data!!');
			}
		},

        /**
         * delete fund code
         * @param { number } id - id of the fund code to be deleted
         */
		async deleteProfileType(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/workflow/fund_code/delete/${id}`
				);
				if (response.data.success) {
					toastr.success('Fund Code was successfuly deleted');
					this.fundCodes = this.fundCodes.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
				} else {
					toastr.error('There was a problem deleting fund Code!!');
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
