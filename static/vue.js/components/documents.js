Vue.use(VeeValidate);
Vue.component('ValidationProvider', VeeValidate.ValidationProvider);
Vue.component('v-select', VueSelect.VueSelect);
Vue.component('modal', {
  template: '#modal-template',
});

// start app
new Vue({
  delimiters: ['[[', ']]'],
  el: '#documents',
  data: {
    showModal: false,
    programs_list: [],
    name: '',
    url: '',
    description: '',
    parent_id: '',
    program_id: '',
    isEdit: false,
    modalHeader: 'Add new document',
    filtered_program: false,
    filtered_program_id: 0
  },
  beforeMount: function () {

    this.makeRequest('GET', '/workflow/level1/')
      .then(response => {
        if (response.data) {
          this.programs_list = response.data.map(el => {
            el['program_id'] = el['id'];
            delete el['id'];
            return el;
          });
        }
      })
      .catch(e => {
        toastr.error('There was a problem loading data from the database');
      });

    $('#documentationtable').DataTable();

  },

  methods: {
    /**
     * open or close the document form modal
     * @param { object } item - document item
     */
    toggleModal: function (item = null) {
      this.showModal = !this.showModal;
      if (item) {
        this.isEdit = true;
        this.modalHeader = `Edit ${item.name}`;
        this.name = item.name;
        this.description = item.description;
        this.program_id = item.program_id;
      } else {
        this.isEdit = false;
        this.name = '';
        this.description = '';
        this.program_id = '';
        this.modalHeader = 'Add new document';
      }
    },

    /**
     * Format date
     * @param {string} date - date to be formatted
     */
    formatDate: function (date) {
      return moment(date, 'YYYY-MM-DDThh:mm:ssZ').format('YYYY-MM-DD');
    },

    /**
     * process form data
     * @param { boolean } saveNew - true to keep the modal open for additional posts
     */
    processForm: function (saveNew = false) {
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
     * Create new document
     * @param { boolean } saveNew - true if a user wants to make multiple documents
     */
    async postData(saveNew) {
      let csrfmiddlewaretoken = document.querySelectorAll("input[name=csrfmiddlewaretoken]")[0].value
      let data = {
        name: this.name,
        url: this.url,
        program: this.program_id.toString(),
        csrfmiddlewaretoken
      }
      console.log('heyy',data)
      // return;
      try {
        const response = await this.makeRequest(
          'POST',
          "/workflow/documentation/add",
          data
        );
        if (response) {
          toastr.success('Documentation was added successfully');
          response.data['program_id'] = response.data['program'];
          delete response.data['program'];
          this.setFilter(this.filtered_program_id);
          if (!saveNew) {
            this.toggleModal();
          }
          // resetting the form
          this.name = '';
          this.url = '';
          this.program_id = '';
          this.$validator.reset();

          const urlWithoutQueryString = window.location.href.split('?')[0];
          if (saveNew) {
            window.location.replace(`${urlWithoutQueryString}?quick-modal=true`);
          } else {
            setTimeout(() => {
              window.location.replace(urlWithoutQueryString);
            }, 2000);
          }
        }
      } catch (error) {
        toastr.error('There was a problem saving');
      }
    },

    // Set workflow level 1 filter
    setFilter: function (id) {
      this.filtered_program = true;
      this.filtered_program_id = id;
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

    blur(field) {
      const provider = this.$refs[field];
      return provider.validate();
    }
  },

  computed: {
    /**
     * Check if document form is valid
     */
    isFormValid() {
      return this.name && this.program_id && this.url;
    }
  }
});
