Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#indicator_type',
	data: {
		showModal: false,
        showDeleteModal: false,
        indicatorTypes: [],
        name: '',
        description: '',
		isEdit: false,
		currentIndicatorType: null,
        itemToDelete: null,
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/indicators/indicator_type/list')
			.then(response => {
				if (response.data) {
                    this.indicatorTypes = response.data.sort((a, b) => b.id - a.id);
                    this.modalHeader = 'Add Indicator Type'; 
					$(document).ready(() => {
						$('#indicatorTypesTable').DataTable({
                            pageLength: 5,
                            lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading indicator types from the database!!');
				this.indicatorTypes = [];
			});
	},
	methods: {
        /**
         * open or close the indicator type form modal
         * @param { object } item - indicator type item
         */
		toggleModal: function(item = null) {
            this.showModal = !this.showModal;
			if (item) {
                this.isEdit = true;
				this.modalHeader = `Edit ${item.indicator_type}`;
				this.currentIndicatorType = item;
                this.name = item.indicator_type;
                this.description = item.description;
			}
		},

        /**
         * open or close the indicator type delete modal
         * @param { object } data - indicator type item
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
					if (this.currentIndicatorType && this.currentIndicatorType.id) {
						this.updateIndicatorType();
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
         * create new indicator type
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/indicators/indicator_type/add`,
					{
                        name: this.name,
                        description: this.description
					}
                );
				if (response) {
                    toastr.success('Indicator type successfuly saved');
					this.indicatorTypes.unshift(response.data);
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
         * edit indicator type item
         */
		async updateIndicatorType() {
			try {
				const response = await this.makeRequest(
					'PUT',
					`/indicators/indicator_type/edit/${this.currentIndicatorType.id}`,
					{ 
                        name: this.name, 
                        description: this.description,
                    }
				);
				if (response) {
					toastr.success('Indicator type was successfuly updated');
					const newIndicatorTypes = this.indicatorTypes.filter(item => {
						return item.id != this.currentIndicatorType.id;
					});
					this.indicatorTypes = newIndicatorTypes;
					this.indicatorTypes.unshift(response.data);
					this.isEdit = false;
                    this.name = null;
                    this.description = null;
					this.modalHeader = 'Add Indicator Type';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data!!');
			}
		},

        /**
         * delete indicator type
         * @param { number } id - id of the indicator type to be deleted
         */
		async deleteProfileType(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/indicators/indicator_type/delete/${id}`
				);
				if (response.data.success) {
					toastr.success('Indicator type was successfuly deleted');
					this.indicatorTypes = this.indicatorTypes.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
				} else {
					toastr.error('There was a problem deleting indicator type!!');
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
         * Check if indicator type form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
