Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#program_fund_code',
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
					// $(document).ready(() => {
					// 	$('#fundCodesTable').DataTable({
                    //         pageLength: 5,
                    //         lengthMenu: [5, 10, 15, 20]
					// 	});
					// });
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
					this.addFundCodeOptions(response.data);
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
		add the created fundcode to select options
		**/
		addFundCodeOptions(fundCode) {
			codeSelect2 = $('#id_fund_code');
			var option = new Option(fundCode.name, fundCode.id, true, true);
			codeSelect2.append(option).trigger('change');
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
