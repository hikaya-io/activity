Vue.component('indicator tracking', {
    delimiters: ['[[', ']]'],
    el: '#indicator_tracking_tables',
    data: {

    },

    beforeMount: function() {

    },
    methods: {
        makeRequest(method, url, data = null) {
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';
            axios.defaults.xsrfCookieName = 'csrftoken';
            return axios({method, url, data});
        },
        
    },
  });