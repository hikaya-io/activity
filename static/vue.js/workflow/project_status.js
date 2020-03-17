Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#project_status',
	data: {
		showModal: false,
        showDeleteModal: false,
        projectStatuses: [],
        name: '',
        description: '',
		isEdit: false,
		currentProjectStatus: null,
        itemToDelete: null,
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/project_status/')
			.then(response => {
				if (response.data) {
                    this.projectStatuses = response.data.sort((a, b) => b.id - a.id);
                    this.modalHeader = 'Add Project Status';
					$(document).ready(() => {
						$('#projectStatusTable').DataTable({
                            pageLength: 5,
                            lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading project statuses from the database');
				this.projectStatuses = [];
			});
	},
	methods: {
        /**
         * open or close the project status form modal
         * @param { object } item - project status item
         */
		toggleModal: function(item = null) {
            this.showModal = !this.showModal;
			if (item) {
                this.isEdit = true;
				this.modalHeader = `Edit ${item.name}`;
				this.currentProjectStatus = item;
                this.name = item.name;
                this.description = item.description;
			} else {
				this.isEdit = false;
				this.modalHeader = 'Add project status';
				this.currentProjectStatus = null;
                this.name = null;
                this.description = null;
			}
		},

        /**
         * open or close the project status delete modal
         * @param { object } data - project status item
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
					if (this.currentProjectStatus && this.currentProjectStatus.id) {
						this.updateProjectStatus();
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
         * create new project status
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/workflow/project_status/`,
					{
                        name: this.name,
                        description: this.description
					}
                );
				if (response) {
                    toastr.success('Project status successfully saved');
					this.projectStatuses.unshift(response.data);
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
         * edit project status item
         */
		async updateProjectStatus() {
			try {
				const response = await this.makeRequest(
					'PATCH',
					`/workflow/project_status/${this.currentProjectStatus.id}`,
					{
                        name: this.name,
                        description: this.description,
                    }
				);
				if (response) {
					toastr.success('Project status was successfully updated');
					const newprojectStatuses = this.projectStatuses.filter(item => {
						return item.id != this.currentProjectStatus.id;
					});
					this.projectStatuses = newprojectStatuses;
					this.projectStatuses.unshift(response.data);
					this.isEdit = false;
                    this.name = null;
                    this.description = null;
                    this.currentProjectStatus = null;
					this.modalHeader = 'Add project status';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data');
			}
		},

        /**
         * delete project status
         * @param { number } id - id of the project status to be deleted
         */
		async deleteProfileType(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/workflow/project_status/${id}`
				);
				if (response.status === 204) {
					toastr.success('Project status was successfully deleted');
					this.projectStatuses = this.projectStatuses.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
					this.modalHeader = 'Add project status';
					this.itemToDelete = null;
				} else {
					toastr.error('There was a problem deleting project status');
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
         * Check if project status form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
