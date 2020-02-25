Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#data_collection_frequency',
	data: {
		showModal: false,
		showDeleteModal: false,
		frequency: '',
		description: '',
		frequencies: [],
		isEdit: false,
		currentFrequency: null,
		itemToDelete: null,
		modalHeader: 'Add data collection frequency',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/indicators/data_collection_frequency/list')
			.then(response => {
				if (response.data) {
					this.frequencies = response.data.sort((a, b) => b.id - a.id);
					$(document).ready(() => {
						$('#dataCollectionFrequencyTable').DataTable({
							pageLength: 5,
							lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading frequencies from the database');
				this.frequencies = [];
			});
	},
	methods: {
        /**
         * open or close the frequency form modal
         * @param { object } item - frequency item
         */
		toggleModal: function(item = null) {
			this.showModal = !this.showModal;
			if (item) {
				this.isEdit = true;
				this.modalHeader = `Edit ${item.frequency}`;
				this.currentFrequency = item;
				this.frequency = item.frequency;
				this.description = item.description;
			} else {
				this.isEdit = false;
				this.modalHeader = `Add data collection frequency`;
				this.currentFrequency = null;
				this.frequency = null;
				this.description = null;
			}
		},

        /**
         * open or close the frequency delete modal
         * @param { object } data - frequency item
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
					if (this.currentFrequency && this.currentFrequency.id) {
						this.updateFrequency();
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
         * create new Data Collection Frequencies
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/indicators/data_collection_frequency/add`,
					{
						frequency: this.frequency,
						description: this.description
					}
				);
				if (response) {
                    toastr.success('Data collection frequency is saved');
					this.frequencies.unshift(response.data);
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.frequency = '';
					this.description = '';
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving');
			}
		},

        /**
         * edit Data Collection Frequency item
         */
		async updateFrequency() {
			try {
				const response = await this.makeRequest(
					'PUT',
					`/indicators/data_collection_frequency/edit/${this.currentFrequency.id}`,
					{ frequency: this.frequency, description: this.description }
				);
				if (response) {
					toastr.success('Data collection frequency is updated');
					const newFrequencies = this.frequencies.filter(item => {
						return item.id != this.currentFrequency.id;
					});
					this.frequencies = newFrequencies;
					this.frequencies.unshift(response.data);
					this.isEdit = false;
					this.frequency = null;
					this.modalHeader = 'Add data collection frequency';
					this.description = null;
					this.currentFrequency = null;

					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating this');
			}
		},

        /**
         * delete collection data frequency
         * @param { number } id - id of the frequency to be deleted
         */
		async deleteFrequency(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/indicators/data_collection_frequency/delete/${id}`
				);
				if (response.data.success) {
					toastr.success('Data collection frequency is deleted');
					this.frequencies = this.frequencies.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
					this.modalHeader = 'Add data collection frequency';
					this.itemToDelete = null;
				} else {
					toastr.error('There was a problem deleting this');
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
         * @return { Promise } - axios response ePromise
         */
		makeRequest(method, url, data = null) {
			axios.defaults.xsrfHeaderName = 'X-CSRFToken';
			axios.defaults.xsrfCookieName = 'csrftoken';
			return axios({ method, url, data });
		},
	},

	computed: {
        /**
         * Check if frequency form is valid
         */
		isFormValid() {
			return this.frequency;
		},
	},
});
