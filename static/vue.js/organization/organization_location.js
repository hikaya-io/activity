Vue.use(VeeValidate);
Vue.component('v-select', VueSelect.VueSelect);

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
		admin_boundary: '',
		zoom: null,
		adminBoundaries: [
			{label: 'ADM0', value: 'ADM0'},
			{label: 'ADM1', value: 'ADM1'},
			{label: 'ADM2', value: 'ADM2'},
			{label: 'ADM3', value: 'ADM3'}
		],
		showAdminBoundary: false
	},
	beforeMount: function() {
		this.makeRequest('GET', '/workflow/organization/?user_org=true')
			.then(response => {
				if (response.data) {
					this.organization = response.data[0];
					this.setOrganizationFields(response.data[0])
					this.showTheMap()
				}
			})
			.catch(e => {
				console.log(e)
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
				console.log(e);
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
				}
			})
			.catch(e => {
				this.countries = [];
			});
		},

		/**
		 * Call this function to draw thw map
		 */
		showTheMap(adminBoundary=null, geoJsonData=null) {
			var container = L.DomUtil.get('org_map');
			if(container != null){
				container._leaflet_id = null;
			} 
			let map = L.map('org_map').setView(
				[
					this.latitude ? this.latitude : 0.00, 
					this.longitude ? this.longitude : 0.00
				], 
				this.zoom ? this.zoom : 5
				);

			L.tileLayer(
				'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
					'attribution': 'Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
				}
			).addTo(map);
			
			if (adminBoundary) {
				var myStyle = {
					"color": "#00ff00",
					"weight": 5,
					"opacity": 0.9
				};
				
				L.geoJSON(geoJsonData, {
					style: myStyle
				}).addTo(map);
			}
		},

		/**
		 * on select of a country
		 * @param {array} selectedValues
		 */
		countryCodeSelected(value) {
			this.showAdminBoundary = true;
		},

		/**
		 * Render country Boundary
		 */
		renderCounntryBoundaries(value) {
			console.log(value)
			this.getBoundaryData(value);

		},

		getBoundaryData(admin) {
			let data = null;
			const country = this.countries.find(item => item.id === +this.country_code[0]);
			console.log('Country:::', country)
			this.makeRequest(
				'GET', 
				`https://raw.githubusercontent.com/hikaya-io/admin-boundaries/master/data/${
					country.code.toUpperCase()
				}/${
					admin.toUpperCase()
				}/${country.code.toUpperCase()}_${admin.toUpperCase()}.geojson`
			)
			.then(response => {
				data = response.data;
				this.showTheMap(admin, data);
				console.log('Dataaa:::', response)
			})
			.catch(e => {
				console.log(e)
				toastr.error('There was a problem loading boundary data for the country');
			});
			return data;

		}
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
