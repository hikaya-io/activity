Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#level',
	data: {
		showModal: false,
		showDeleteModal: false,
		levels: [],
        name: '',
		description: '',
		sort: null,
		isEdit: false,
		currentLevel: null,
        itemToDelete: null,
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', '/indicators/level/')
			.then(response => {
				if (response.data) {
                    this.levels = response.data.sort((a, b) => b.id - a.id);
                    this.modalHeader = 'Add Level'; 
					$(document).ready(() => {
						$('#levelsTable').DataTable({
                            pageLength: 5,
                            lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading levels from the database!!');
				this.levels = [];
			});
	},
	methods: {
        /**
         * open or close the level form modal
         * @param { object } item - level item
         */
		toggleModal: function(item = null) {
            this.showModal = !this.showModal;
			if (item) {
				this.isEdit = true;
				this.modalHeader = `Edit ${item.name}`;
				this.currentLevel = item;
                this.name = item.name;
				this.description = item.description;
				this.sort = item.sort;
			} else {
				this.isEdit = false;
				this.modalHeader = 'Add Level';
				this.currentLevel = null;
                this.name = null;
				this.description = null;
				this.sort = null;
			}
		},

        /**
         * open or close the level delete modal
         * @param { object } data - level item
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
					if (this.currentLevel && this.currentLevel.id) {
						this.updateLevel();
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
         * create new level
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			try {
				const response = await this.makeRequest(
					'POST',
					`/indicators/level/`,
					{
                        name: this.name,
						description: this.description,
						sort: this.sort
					}
                );
				if (response) {
                    toastr.success('Level successfully saved');
					this.levels.unshift(response.data);
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
                    this.name = '';
					this.description = '';
					this.sort = null;
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data');
			}
		},

        /**
         * edit Level item
         */
		async updateLevel() {
			try {
				const response = await this.makeRequest(
					'PATCH',
					`/indicators/level/${this.currentLevel.id}`,
					{ 
                        name: this.name, 
						description: this.description,
						sort: this.sort
                    }
				);
				if (response) {
					toastr.success('Level was successfully updated');
					const newLevels = this.levels.filter(item => {
						return item.id != this.currentLevel.id;
					});
					this.levels = newLevels;
					this.levels.unshift(response.data);
					this.isEdit = false;
                    this.name = '';
					this.description = '';
					this.sort = null;
					this.currentLevel = null;
					this.modalHeader = 'Add Level';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data');
			}
		},

        /**
         * delete level
         * @param { number } id - id of the level to be deleted
         */
		async deleteProfileType(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/indicators/level/${id}`
				);
				if (response.status === 204) {
					toastr.success('Level was successfully deleted');
					this.levels = this.levels.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
					this.modalHeader = 'Add Level';
					this.itemToDelete = null;
				} else {
					toastr.error('There was a problem deleting level');
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
         * @return { Promise } - axios response Promise
         */
		makeRequest(method, url, data = null) {
			axios.defaults.xsrfHeaderName = 'X-CSRFToken';
			axios.defaults.xsrfCookieName = 'csrftoken';
			return axios({ method, url, data });
		},
	},

	computed: {
        /**
         * Check if level form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
