Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#profile_type',
	data: {
		showModal: false,
		showDeleteModal: false,
		profile: '',
		profileTypes: [],
		isEdit: false,
		currentProfileType: null,
        itemToDelete: null,
        siteLabel: '',
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/profile_type/list')
			.then(response => {
				if (response.data) {
                    this.profileTypes = response.data.profile_types.sort((a, b) => b.id - a.id);
                    this.siteLabel = response.data.site_label;
                    this.modalHeader = `Add ${this.siteLabel} Type`; 
					$(document).ready(() => {
						$('#profileTypesTable').DataTable({
                            pageLength: 5,
                            lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading profile types from the database!!');
				this.profileTypes = [];
			});
	},
	methods: {
        /**
         * open or close the profile type form modal
         * @param { object } item - profile type item
         */
		toggleModal: function(item = null) {
			this.showModal = !this.showModal;
			if (item) {
				this.isEdit = true;
				this.modalHeader = `Edit ${item.profile}`;
				this.currentProfileType = item;
				this.profile = item.profile;
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
         * Format date
         * @param {string} date - date to be formatted
         */
        formatDate: function(date) {
            return moment(date, 'YYYY-MM-DDThh:mm:ssZ').format('YYYY-MM-DD');
        },

        /**
         * process form data
         * @param { boolen } saveNew - true to keep the modal open for additional posts
         */
		processForm: function(saveNew = false) {
			this.$validator.validateAll().then(result => {
				if (result) {
					if (this.currentProfileType && this.currentProfileType.id) {
						this.updateProfileType();
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
         * create new profile type
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/workflow/profile_type/add`,
					{
						profile: this.profile,
					}
				);
				if (response) {
                    toastr.success('Profile Type Successfuly Saved');
					this.profileTypes.unshift(response.data);
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.profile = '';
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data!!');
			}
		},

        /**
         * edit Profile Type item
         */
		async updateProfileType() {
			try {
				const response = await this.makeRequest(
					'PUT',
					`/workflow/profile_type/edit/${this.currentProfileType.id}`,
					{ profile: this.profile }
				);
				if (response) {
					toastr.success('Profile Type was successfuly Updated');
					const newProfileTypes = this.profileTypes.filter(item => {
						return item.id != this.currentProfileType.id;
					});
					this.profileTypes = newProfileTypes;
					this.profileTypes.unshift(response.data);
					this.isEdit = false;
					this.profile = null;
					this.currentProfileType = null;
					this.modalHeader = 'Add Profile Type';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data!!');
			}
		},

        /**
         * delete profile type
         * @param { number } id - id of the profile type to be deleted
         */
		async deleteProfileType(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/workflow/profile_type/delete/${id}`
				);
				if (response.data.success) {
					toastr.success('Profile Type was successfuly Deleted');
					this.profileTypes = this.profileTypes.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
				} else {
					toastr.error('There was a problem deleting profile type!!');
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
         * Check if profile type form is valid
         */
		isFormValid() {
			return this.profile;
		},
	},
});
