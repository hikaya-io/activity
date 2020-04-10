Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#stakeholder_type',
	data: {
		showModal: false,
		showDeleteModal: false,
        stakeholderTypes: [],
		name: '',
		description: '',
		isEdit: false,
		currentStakeholderType: null,
        itemToDelete: null,
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/stakeholder_type/')
			.then(response => {
				if (response.data) {
                    this.stakeholderTypes = response.data.sort((a, b) => b.id - a.id);
                    this.modalHeader = 'Add Stakeholder Type'; 
					$(document).ready(() => {
						$('#stakeholderTypesTable').DataTable({
                            pageLength: 5,
                            lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading stakeholder types from the database');
				this.stakeholderTypes = [];
			});
	},
	methods: {
        /**
         * open or close the stakeholder type form modal
         * @param { object } item - stakeholder type item
         */
		toggleModal: function(item = null) {
            this.showModal = !this.showModal;
			if (item) {
				this.isEdit = true;
				this.modalHeader = `Edit ${item.name}`;
				this.currentStakeholderType = item;
				this.name = item.name;
				this.description = item.description;
			} else {
				this.isEdit = false;
				this.modalHeader = 'Add Stakeholder Type';
				this.currentStakeholderType = null;
				this.name = null;
				this.description = null;
			}
		},

        /**
         * open or close the stakeholder type delete modal
         * @param { object } data - stakeholder type item
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
					if (this.currentStakeholderType && this.currentStakeholderType.id) {
						this.updateStakeholderType();
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
         * create new stakeholder type
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/workflow/stakeholder_type/`,
					{
						name: this.name,
						description: this.description
					}
                );
				if (response) {
                    toastr.success('Stakeholder type successfuly saved');
					this.stakeholderTypes.unshift(response.data);
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.name = '';
					this.description = '';
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data!!');
			}
		},

        /**
         * edit stakeholder type item
         */
		async updateStakeholderType() {
			try {
				const response = await this.makeRequest(
					'PUT',
					`/workflow/stakeholder_type/${this.currentStakeholderType.id}`,
					{ 
						name: this.name,
						description: this.description, 
                    }
				);
				if (response) {
					toastr.success('Stakeholder Type was successfuly updated');
					const existingStakeholderTypes = this.stakeholderTypes.filter(item => {
						return item.id != this.currentStakeholderType.id;
					});
					this.stakeholderTypes = existingStakeholderTypes;
					this.stakeholderTypes.unshift(response.data);
					this.isEdit = false;
					this.name = null;
					this.description = null;
                    this.currentStakeholderType = null;
					this.modalHeader = 'Add Stakeholder Type';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data');
			}
		},

        /**
         * delete stakeholder type
         * @param { number } id - id of the stakeholder type to be deleted
         */
		async deleteStakeholderType(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/workflow/stakeholder_type/${id}`
				);
				if (response.status === 204) {
					toastr.success('Stakeholder Type was successfuly deleted');
					this.stakeholderTypes = this.stakeholderTypes.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
					this.modalHeader = 'Add Stakeholder Type';
					this.itemToDelete = null;
				} else {
					toastr.error('There was a problem deleting stakeholder type');
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
         * Check if stakeholder type form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
