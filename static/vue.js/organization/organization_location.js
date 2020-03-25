Vue.use(VeeValidate);

// start app
new Vue({
	delimiters: ['[[', ']]'],
	el: '#organizationLocationForm',
	data: {
		organization: null,
		countries: [],
        country_code: '',
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
					this.setOrganizationFields(response.data[0])
					this.showTheMap()
				}
			})
			.catch(e => {
				toastr.error('There was a problem loading organization location from the database!');
				this.organization = null;
			});
		// load countries
		this.loadCountries();
		
	},
	methods: {

        /**
         * edit organization location
         */
		async updateLocation() {
			try {
				const response = await this.makeRequest(
					'PATCH',
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
					toastr.success('Organization location was successfully updated');
					this.organization = response.data
					this.setOrganizationFields(response.data)
				}
			} catch (e) {
				toastr.error('There was a problem updating your data');
			}
		},

		/**
         * Cancel edit organization location
         */
		cancelLocationUpdate() {
			this.setOrganizationFields(this.organization)
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

		/**
		 * set organization fields
		 * @param { object } orgObject
		 */
		setOrganizationFields(orgObject) {
			this.country_code = orgObject.country_code;
			this.location_description = orgObject.location_description;
			this.latitude = orgObject.latitude;
			this.longitude = orgObject.longitude;
			this.zoom = orgObject.zoom;
		},

		/**
		 * Load all coutries to populate the dropdown
		 */
		loadCountries() {
			this.makeRequest('GET', '/workflow/countries')
			.then(response => {
				if (response.data) {
					this.countries = response.data;
					// $(document).ready(() => {
					// 	$('#country_code').select2({
					// 		theme: 'bootstrap'
					// 	});
					// });
				}
			})
			.catch(e => {
				this.countries = [];
			});
		},

		/**
		 * Call this function to draw thw map
		 */
		showTheMap() {
			var container = L.DomUtil.get('org_map');
			if(container != null){
				container._leaflet_id = null;
			} 
			let map = L.map('org_map').setView(
				[
					this.latitude, 
					this.longitude
				], 
				this.zoom
				);

			L.tileLayer(
				'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
					'attribution': 'Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
				}
			).addTo(map);
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
