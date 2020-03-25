Vue.use(VeeValidate);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#level_1_modal',
	components: {
		vuejsDatepicker
	},
	data: {
        name: '',
		sectors: [],
		start_date: '',
		end_date: '',
		sectorsList: [],
		level_1_label: '',
		showModal: false,
		isEdit: false,
		currentProgram: null,
		modalHeader: '',
		disabledDates: {
			start:{},
			end:{}
		},
		saveNew: false,
	},
	beforeMount: function() {
		console.log('saveNew : ', this.saveNew);
		this.makeRequest('GET', '/workflow/level1_dependant_data')
			.then(response => {
				if (response.data) {
					console.log('response.data : ', response.data)
					this.level_1_label = response.data.level_1_label;
					this.modalHeader = `Add ${this.level_1_label}`; 
					this.sectorsList = response.data.sectors;

					$(document).ready(() => {
					  
					});
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading programs from the database!!');
			});
	},
	methods: {
        /**
         * open or close the fund code form modal
         * @param { object } item - fund code item
         */
		toggleModal: function(item = null) {
			this.showModal = !this.showModal;
			console.log('showModal : ', this.showModal);
			if (item) {
				this.isEdit = true;
				this.modalHeader = `Edit ${item.name}`;
				this.currentProgram = item;
                this.name = item.name;
				this.start_date = item.start_date;
                this.end_date = item.end_date;				
			}
		},

		customFormatter(date) {
			console.log('here : ', moment(date).format('DD.MM.YYYY'))
			return moment(date).format('DD.MM.YYYY');
		},

        /**
         * process form data
         * @param { boolean } saveNew - true to keep the modal open for additional posts
         */
		processForm: function(saveNew = false) {
			this.saveNew = saveNew;
			this.$validator.validateAll().then(result => {
				if (result) {
					if (saveNew) {
						this.postData(saveNew);
					} else {
						this.postData();
					}
				}
			});
		},

        /**
         * create new fund code
         * @param { boolean } saveNew - true if a user wants to make multiple posts
         */
		async postData(saveNew) {
			console.log('date : ', moment(this.start_date, 'DD.MM.YYYY').format('YYYY-MM-DDThh:mm:ssZ'))
			console.log('saveNew : ', saveNew);
			try {
				const response = await this.makeRequest(
					'POST',
					`/workflow/level1/add`,
					{
						program_name: this.name,
						sectors: this.sectors,
						start_date: this.start_date ? moment(this.start_date, 'DD.MM.YYYY').format('YYYY-MM-DDThh:mm:ssZ') : null,
                        end_date: this.end_date ? moment(this.end_date, 'DD.MM.YYYY').format('YYYY-MM-DDThh:mm:ssZ') : null
					}
                );
				if (response) {
					toastr.success(`${this.level_1_label} successfuly saved`);
					location.reload();
					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.name = '';
					this.sectors = [];
					this.start_date = '';
					this.end_date = '';
					this.$validator.reset();
				}
			} catch (error) {
				toastr.error('There was a problem saving your data!!');
			}
		},

		 /**
		add the created fundcode to select options
		**/
		// addFundCodeOptions(fundCode) {
		// 	codeSelect2 = $('#id_fund_code');
		// 	var option = new Option(fundCode.name, fundCode.id, true, true);
		// 	codeSelect2.append(option).trigger('change');
		// },

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

		disableDates(date, value) {
			console.log('Event', new Date(value))
			if(date === 'start') {
				this.disabledDates.end = {
					to: new Date(value)
				}
			} else {
				this.disabledDates.start = {
					from: new Date(value)
				}
			}
		}
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
