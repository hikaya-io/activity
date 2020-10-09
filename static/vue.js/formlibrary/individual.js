Vue.use(VeeValidate);
Vue.component('ValidationProvider', VeeValidate.ValidationProvider);
Vue.component('v-select', VueSelect.VueSelect);
Vue.component('modal', {
	template: '#modal-template',
});

// start app
new Vue({
  delimiters: ['[[', ']]'],
  el: '#individual_list',
  data:{
    level_1_label: '',
    individual_label: '',
    modalHeader: '',
    create_data: {
      first_name : '',
      last_name : '',
      date_of_birth : '',
      id_number : 0,
      primary_phone : '',
      sex : '',
      program: 0,
    },
    individualsList: [],
    trainingList:[],
    distributionsList:[],
    programsList:[],
    programs: [],
    showModal: false,
    isEdit: false,
    saveNew: false,
		showDeleteModal: false,
    itemToDelete: null,
  },
  beforeMount: function() {
    this.makeRequest('GET', '/formlibrary/individual_data')
    .then(response => {
      if (response.data) {
        this.level_1_label = response.data.level_1_label;
        this.individual_label = response.data.individual_label;
        this.modalHeader = `Add ${this.individual_label}`; 
        this.programsList = response.data.programs.sort((a, b) => (a.name > b.name) ? 1 : -1);
        this.individualsList = response.data.individuals;
        this.trainingList = response.data.trainings;
        this.distributionsList = response.data.distributions;

        $(document).ready(() => {
						$('#individualsTable').DataTable({
              pageLength: 10,
              lengthMenu: [10, 15, 20]
						});
					});
      }
    })
    .catch(e => {
      toastr.error('There was a problem loading individuals from the database');
    })
  },
  methods: {
    /**
    * open or close the fund code form modal
    * @param { object } item - fund code item
    */
		toggleModal: function(item = null) {
			this.showModal = !this.showModal;
			this.modalHeader = `Add ${this.individual_label}`; 
			if (!item) {
				this.create_data = {
          first_name : '',
          last_name : '',
          date_of_birth : '',
          id_number : 0,
          primary_phone : '',
          sex : '',
          program: 0,
        }
			}
		},
    /**
    * Format date
    * @param {string} date - date to be formatted
    */
    formatDate: function(date) {
        return date ? moment(date, 'YYYY-MM-DDThh:mm:ssZ').format('YYYY-MM-DD') : '';
    },

		customFormatter(date) {
			return moment(date).format('DD.MM.YYYY');
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
    * process form data
    * @param { boolean } saveNew - true to keep the modal open for additional posts
    */
		processForm: function(saveNew = false) {
			this.saveNew = saveNew;
      if (saveNew) {
        this.postData(saveNew);
      } else {
        this.postData();
      }
		},

    /**
    * create new fund code
    * @param { boolean } saveNew - true if a user wants to make multiple posts
    */
		async postData(saveNew) {
      try {
        const response = await this.makeRequest(
					'POST',
					`/formlibrary/individual/`,
					this.create_data
                );
				if (response.data) {
					toastr.success(`${this.level_1_label} ${this.name} successfully saved`);
					this.individualsList.unshift(response.data);

					if (!saveNew) {
						this.toggleModal();
					}
					// resetting the form
					this.create_data = {
            first_name : '',
            last_name : '',
            date_of_birth : '',
            id_number : 0,
            primary_phone : '',
            sex : '',
            program: 0,
          }
					this.$validator.reset();
				}
      } catch (error) {
        toastr.error('There was a problem saving your data');
      }
    },

    /**
    * delete program
    * @param { number } id - id of the program to be deleted
    */
		toggleDeleteModal: function(data) {
			this.showDeleteModal = !this.showDeleteModal;
			this.modalHeader = 'Confirm delete';
			this.itemToDelete = data;
    },

    /**
    * delete program
    * @param { number } id - id of the program to be deleted
    */
		async deleteProgram(id) {
			try {
				const response = await this.makeRequest(
					'DELETE',
					`/formlibrary/individual/${id}`
				);
				if (response.status === 204) {
					toastr.success(`${this.level_1_label} was successfully deleted`);
					this.individualsList = this.individualsList.filter(item => +item.id !== +id);
					this.showDeleteModal = !this.showDeleteModal;
					this.modalHeader = `Add ${this.level_1_label}`; 
					this.itemToDelete = null;
				} else {
					toastr.error('There was a problem deleting program');
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
			return this.create_data.program;
		},
	},
})