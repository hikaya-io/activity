Vue.use(VeeValidate);
Vue.component('ValidationProvider', VeeValidate.ValidationProvider);
Vue.component('v-select', VueSelect.VueSelect);
Vue.component('modal', {
    template: '#modal-template',
});

// start app
new Vue({
    delimiters: ['[[', ']]'],
    el: '#service_list',
    data: {
        level_1_label: '',
        individual_label: '',
        modalHeader: '',
        training_data: {
            name: "",
            program_id: 0,
            start_date: "",
            end_date: "",
            duration: 0,
        },
        distribution_data: {
            name: "",
            program_id: 0,
            start_date: "",
            end_date: "",
            duration: 0,
            quantity: "",
            item_distributed: "",
        },
        showModal: false,
        isEdit: false,
        saveNew: false,
        showDeleteModal: false,
        itemToDelete: null,
    },
    beforeMount: function() {
        this.individual_label = 'Service';
        this.modalHeader = `Add Service`;
    },
    methods: {
        /**
         * open or close the fund code form modal
         * @param { object } item - fund code item
         */
        toggleModal: function(item = null) {
            this.showModal = !this.showModal;
            this.modalHeader = `Add Service`;
            // if (!item) {
            //     this.create_data = {
            //         first_name: '',
            //         last_name: '',
            //         date_of_birth: '',
            //         id_number: 0,
            //         primary_phone: '',
            //         sex: '',
            //         program: 0,
            //     }
            // }
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

        },

        /**
         * delete service
         * @param { number } id - id of the service to be deleted
         */
        async deleteService(id) {},

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
            return axios({
                method,
                url,
                data
            });
        },
    },
    computed: {
        /**
         * Check if fund code form is valid
         */
        isFormValid() {
            // return this.create_data.program;
        },
    },
})