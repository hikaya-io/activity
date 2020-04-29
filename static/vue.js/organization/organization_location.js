Vue.use(VeeValidate);
Vue.component('v-select', VueSelect.VueSelect);

// start app
new Vue({
    delimiters: ['[[', ']]'],
    el: '#organizationLocationForm',
    data: {
        organization: null,
        countries: [],
        countriesData: [],
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
            {label: 'ADM3', value: 'ADM3'},
        ],
        showAdminBoundary: false,
    },
    beforeMount: function () {
        // load countries
        this.loadCountries();

        this.makeRequest('GET', '/workflow/organization/?user_org=true')
            .then((response) => {
                if (response.data) {
                    this.organization = response.data[0];
                    this.setOrganizationFields(response.data[0]);
                    if (this.organization.admin_boundary) {
                        this.showAdminBoundary = true;
                        this.getBoundaryData(this.organization.admin_boundary);
                    }
                }
            })
            .catch((e) => {
                toastr.error(
                    'There was a problem loading organization location from the database!'
                );
                this.organization = null;
            });
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
                        latitude: this.latitude !== '' ? this.latitude : null,
                        longitude: this.longitude !== '' ? this.longitude : null,
                        zoom: this.zoom,
                        admin_boundary: this.admin_boundary,
                    }
                );
                if (response) {
                    toastr.success('Organization location was successfully updated');
                    this.organization = response.data;
                    this.setOrganizationFields(response.data);
                }
            } catch (e) {
                toastr.error('There was a problem updating your data');
            }
        },

        /**
         * Cancel edit organization location
         */
        cancelLocationUpdate() {
            this.setOrganizationFields(this.organization);
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
            return axios({method, url, data});
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
            this.admin_boundary = orgObject.admin_boundary;
        },

        /**
         * Load all coutries to populate the dropdown
         */
        loadCountries() {
            this.makeRequest('GET', '/workflow/countries')
                .then((response) => {
                    if (response.data) {
                        this.countries = response.data;
                    }
                })
                .catch((e) => {
                    this.countries = [];
                });
        },

        /**
         * Call this function to draw thw map
         */
        showTheMap(adminBoundary = null, geoJsonData = null) {
            const container = L.DomUtil.get('org_map');
            if (container != null) {
                container._leaflet_id = null;
            }
            let map = L.map('org_map').setView(
                [this.latitude ? this.latitude : 0.0, this.longitude ? this.longitude : 0.0],
                this.zoom ? this.zoom : 5
            );

            L.tileLayer(
                'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
                {
                    attribution:
                        'Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
                }
            ).addTo(map);

            if (adminBoundary) {
                var myStyle = {
                    color: '#00CCCC',
                    weight: 2,
                    opacity: 0.5,
                };

                L.geoJSON(geoJsonData, {
                    style: myStyle,
                }).addTo(map);
            }
        },

        /**
         * on select of a country
         * @param {array} selectedValues
         */
        countryCodeSelected(value) {
            let selectedCountry = null;
            if (value.length > 0) {
                selectedCountry = this.countries.find(
                    country => +country.id === +value[value.length - 1]
                )
                this.latitude = selectedCountry.latitude;
                this.longitude = selectedCountry.longitude;
            }
            this.showAdminBoundary = true;
            if (this.admin_boundary) {
                this.getBoundaryData(this.admin_boundary, selectedCountry);
            }
        },

        /**
         * Render country Boundary
         */
        renderCountryBoundaries(value) {
            this.getBoundaryData(value);
        },

        /**
         * Load
         */
        getBoundaryData(admin, country=null) {
            let data = null;
            if (this.admin_boundary && this.country_code.length) {
                if(!country) {

                    const code = this.country_code[this.country_code.length - 1]
                    country = this.countries.find((item) => item.id === +code);
                }
                if (country) {
                    this.makeRequest(
                        'GET',
                        `https://raw.githubusercontent.com/hikaya-io/admin-boundaries/master/data/${country.code.toUpperCase()}/${admin.toUpperCase()}/${country.code.toUpperCase()}-${admin.toUpperCase()}.geojson`
                    )
                        .then((response) => {
                            data = response.data;
                            this.showTheMap(admin, data);
                        })
                        .catch((e) => {
                            toastr.error(
                                'There was a problem loading boundary data for the country'
                            );
                            this.showTheMap();
                        });
                }
            } else {
                this.showTheMap();
            }
        },

        /**
         * Load geoJson data for the selected countries
         */
        loadBoundaryData() {
            this.countriesData = [];
            if (this.country_code) {
                this.country_code.forEach((code) => {
                    let data = null;
                    const country = this.countries.find(
                        (item) => item.id === +this.country_code[0]
                    );
                    this.makeRequest(
                        'GET',
                        `https://raw.githubusercontent.com/hikaya-io/admin-boundaries/master/data/${country.code.toUpperCase()}/${admin.toUpperCase()}/${country.code.toUpperCase()}_${admin.toUpperCase()}.geojson`
                    )
                        .then((response) => {
                            data = response.data;
                            this.countriesData.push(data);
                        })
                        .catch((e) => {
                            toastr.error(
                                'There was a problem loading boundary data for the country'
                            );
                        });
                });
            }
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
