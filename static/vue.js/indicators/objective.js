Vue.use(VeeValidate);
Vue.component('modal', {
  template: '#modal-template'
});

// start app
new Vue({
  delimiters: ['[[', ']]'],
  el: '#objective',
  data: {
    showModal: false,
    showDeleteModal: false,
    objectives: [],
    programs_list: [],
    name: '',
    description: '',
    parent: '',
    program: '',
    isEdit: false,
    currentObjective: null,
    itemToDelete: null,
    modalHeader: 'Add objective'
  },
  beforeMount: function() {
    this.makeRequest('GET', '/indicators/objective/list')
      .then(response => {
        console.log('objective list', response.data);
        if (response.data) {
          this.objectives = response.data.objectives.sort(
            (a, b) => b.id - a.id
          );
          this.programs_list = response.data.programs_list;
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
        toastr.error(
          'There was a problem loading objectives from the database'
        );
        this.objectives = [];
      });

    //   this.makeRequest('GET', '/indicators/objective/programs')
    //   .then(response => {
    //     console.log('objective list', response.data);
    //     if (response.data) {
    //       this.programs_list = response.data.programs_list;
    //     } 
    //   })
    //   .catch(e => {
    //     toastr.error(
    //       'There was a problem loading objectives from the database'
    //     );
    //     this.objectives = [];
    //   });
  },
  methods: {
    /**
     * open or close the objective form modal
     * @param { object } item - objective item
     */
    toggleModal: function(item = null) {
      this.showModal = !this.showModal;
      if (item) {
        this.isEdit = true;
        this.modalHeader = `Edit ${item.name}`;
        this.currentObjective = item;
        this.name = item.name;
        this.description = item.description;
        this.program = item.program_id;
        this.parent = item.parent_id;
      } else {
        this.isEdit = false;
        this.name = '';
        this.description = '';
        this.program = '';
        this.parent = '';
        this.modalHeader = 'Add objective';
      }
    },

    /**
     * open or close the objective delete modal
     * @param { object } data - objective item
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
            this.updateObjective();
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
     * Create new objective
     * @param { boolean } saveNew - true if a user wants to make multiple posts
     */
    async postData(saveNew) {
      try {
        const response = await this.makeRequest(
          'POST',
          `/indicators/objective/add`,
          {
            name: this.name,
            description: this.description,
            parent: this.parent,
            program: this.program
          }
        );
        if (response) {
          toastr.success('Objective is saved');
          this.objectives.unshift(response.data);
          if (!saveNew) {
            this.toggleModal();
          }
          // resetting the form
          this.name = '';
          this.description = '';
          this.program = '';
          this.parent = '';
          this.$validator.reset();
        }
      } catch (error) {
        toastr.error('There was a problem saving');
      }
    },

    /**
     * Edit objective item
     */
    async updateObjective() {
      console.log();
      try {
        const response = await this.makeRequest(
          'PUT',
          `/indicators/objective/edit/${this.currentObjective.id}`,
          {
            name: this.name,
            description: this.description,
            parent: this.parent,
            program: this.program
          }
        );
        if (response) {
          toastr.success('Objective is updated');
          const newObjectives = this.objectives.filter(item => {
            return item.id != this.currentObjective.id;
          });
          this.objectives = newObjectives;
          this.objectives.unshift(response.data);
          this.isEdit = false;
          this.name = '';
          this.description = '';
          this.program = '';
          this.parent = '';
          this.currentObjective = null;
          this.modalHeader = 'Add Objective';
          this.toggleModal();
        }
      } catch (e) {
        toastr.error('There was a problem updating this');
      }
    },

    /**
     * Delete objective
     * @param { number } id - id of the objective to be deleted
     */
    async deleteObjective(id) {
      try {
        const response = await this.makeRequest(
          'DELETE',
          `/indicators/objective/delete/${id}`
        );
        if (response.data.success) {
          toastr.success('Objective is deleted');
          this.objectives = this.objectives.filter(item => +item.id !== +id);
          this.showDeleteModal = !this.showDeleteModal;
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
     * @return { Promise } - axios response Promise
     */
    makeRequest(method, url, data = null) {
      axios.defaults.xsrfHeaderName = 'X-CSRFToken';
      axios.defaults.xsrfCookieName = 'csrftoken';
      return axios({ method, url, data });
    }
  },

  computed: {
    /**
     * Check if objective form is valid
     */
    isFormValid() {
      return this.name;
    }
  }
});
