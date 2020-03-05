Vue.use(VeeValidate);

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#organizationLocation',
	data: {
        organization: null,
        country_code: 'test',
		location_description: '',
        latitude: null,
		longitude: null,
		zoom: null,
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/organization/1/?user_org=1')
			.then(response => {
				if (response.data) {
					this.organization = response.data[0];
                    this.country_code = this.organization.country_code;
                    this.location_description = this.organization.location_description;
                    this.latitude = this.organization.latitude;
                    this.longitude = this.organization.longitude;
                    this.zoom = this.organization.zoom;
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading organization location from the database!');
				this.organization = null;
			});
	},
	methods: {
        
        /**
         * Format date
         * @param {string} date - date to be formatted
         */

        /**
         * edit organization location
         */
		updateLocation() {
			alert('am here');
			try {
				const response = this.makeRequest(
					'PUT',
					`/workflow/organization/${this.organization.id}`,
					{
						country_code: this.country_code,
						location_description: this.location_description,
						latitude: this.latitude,
						longitude: this.longitude ,
						zoom: this.zoom
                    }
				);
				if (response) {
					toastr.success('Organization location was successfuly updated');
                    this.country_code = '';
					this.location_description = '';
					this.latitude = '';
				}
			} catch (e) {
				toastr.error('There was a problem updating your data!!');
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
         * Check if organization form is valid
         */
		isFormValid() {
			return this.name;
		},
	},
});
