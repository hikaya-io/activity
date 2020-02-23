Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#objective',
	data: {
		showModal: false,
		showDeleteModal: false,
		objectives: [],
        name: '',
        description: '',
        parent:'',
        create_date:'',
		isEdit: false,
		currentObjective: null,
        itemToDelete: null,
		modalHeader: '',
	},
	beforeMount: function() {
		this.makeRequest('GET', 'indicators/objectives')
			.then(response => {
				if (response.data) {
                    this.objectives = response.data.sort((a, b) => b.id - a.id);
                    this.modalHeader = 'Add objective'; 
					$(document).ready(() => {
						$('#objectivesTable').DataTable({
                            pageLength: 5,
                            lengthMenu: [5, 10, 15, 20]
						});
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading levels from the database');
				this.objectives = [];
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
				this.currentObjective = item;
                this.name = item.name;
				this.description = item.description;
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
					if (this.currentObjective && this.currentObjective.id) {
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
					`/indicators/level/add`,
					{
                        name: this.name,
						description: this.description
					}
                );
				if (response) {
                    toastr.success('Level successfuly saved');
					this.levels.unshift(response.data);
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
         * edit Level item
         */
		async updateLevel() {
			try {
				const response = await this.makeRequest(
					'PUT',
					`/indicators/level/edit/${this.currentObjective.id}`,
					{ 
                        name: this.name, 
						description: this.description,
                    }
				);
				if (response) {
					toastr.success('Level was successfuly updated');
					const newLevels = this.levels.filter(item => {
						return item.id != this.currentObjective.id;
					});
					this.levels = newLevels;
					this.levels.unshift(response.data);
					this.isEdit = false;
                    this.name = '';
					this.description = '';
					this.currentObjective = null;
					this.modalHeader = 'Add Level';
					this.toggleModal();
				}
			} catch (e) {
				toastr.error('There was a problem updating your data!!');
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
					`/indicators/level/delete/${id}`
				);
				if (response.data.success) {
					toastr.success('Level was successfuly deleted');
					this.levels = this.levels.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
				} else {
					toastr.error('There was a problem deleting level!!');
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
         * Check if level form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
