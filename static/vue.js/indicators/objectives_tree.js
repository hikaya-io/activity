Vue.use(VeeValidate);
Vue.component('modal', {
  template: '#modal-template'
});
// Tree component
Vue.component('tree-chart', {
  template: '#vue-tree-template',
  delimiters: ['[[', ']]'],
  props: ["json"],
  data() {
    return {
      treeData: {}
    }
  },
  watch: {
    json: {
      handler: function (Props) {
        let extendKey = function (jsonData) {
          jsonData.extend = (jsonData.extend === void 0 ? true : !!jsonData.extend);
          if (Array.isArray(jsonData.children)) {
            jsonData.children.forEach(c => {
              extendKey(c)
            })
          }
          return jsonData;
        }
        if (Props) {
          this.treeData = extendKey(Props);
        }
      },
      immediate: true
    }
  },
  methods: {
    toggleExtend: function (treeData) {
      treeData.extend = !treeData.extend;
      this.$forceUpdate();
    }
  }
});

// Start vue app
new Vue({
  delimiters: ['[[', ']]'],
  el: '#objectives_tree',
  data: {
    origData: JSON.parse(document.getElementById('objectives-data').textContent),
    treeData: {},
    showModal: false,
    showDeleteModal: false,
    objectives: [],
    programs_list: [],
    parent_obj_list: [],
    name: '',
    description: '',
    parent_id: '',
    program_id: '',
    isEdit: false,
    currentObjective: null,
    itemToDelete: null,
    modalHeader: 'Add objective'
  },
  beforeMount: function () {
    this.makeRequest('GET', '/indicators/objective/list')
      .then(response => {
        if (response.data) {
          this.objectives = response.data.objectives.sort(
            (a, b) => b.id - a.id
          );
          this.parent_obj_list = response.data.objectives.sort(
            (a, b) => b.id - a.id
          );
          this.programs_list = response.data.programs_list;
          this.modalHeader = 'Add objective';
        }
      })
      .catch(e => {
        toastr.error(
          'There was a problem loading objectives from the database'
        );
        this.objectives = [];
      });
  },
  methods: {
    setProgram(id, name) {
      this.currentProgram = name;
      this.currentId = id
      this.refreshTreeData();
    },
    refreshTreeData() {
      this.treeData = this.getChildren('0');
    },
    insertChild(nodeId, child) {
      this.origData[nodeId].children.push(child.id)
      this.origData[`${child.id}`] = {id: child.id, name: child.name, program: this.origData[nodeId].program, children: []}
      this.refreshTreeData()
    },
    getChildren(nodeId) {
      const node = this.origData[nodeId];
      if (node.children.length === 0) {
        return {id: nodeId, name: node.name}
      }
      const children = [];
      for (let i = 0; i < node.children.length; i++) {
        const childId = String(node.children[i]);
        if (this.origData[childId].program !== this.currentProgram) {
          continue
        }
        children.push(this.getChildren(childId));
      }
      return {id: nodeId, name: node.name, children: children}
    },
    toggleModal(treeData) {
      this.showModal = !this.showModal;
      if (this.showModal) {
        if (treeData.id !== '0') {
          this.parent_id = treeData.id
        }
        this.program_id = this.currentId
      }

      this.name = '';
      this.description = '';
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
    async postData(saveNew) {
      try {
        const response = await this.makeRequest(
          'POST',
          `/indicators/objective/add`,
          {
            name: this.name,
            description: this.description,
            parent_id: this.parent_id,
            program_id: this.program_id
          }
        );
        if (response) {
          toastr.success('Objective is saved');
          this.insertChild(this.parent_id, {id: response.data.id, name: response.data.name})
          this.objectives.unshift(response.data);
          if (!saveNew) {
            this.toggleModal();
          }
          // resetting the form
          this.name = '';
          this.description = '';
          this.$validator.reset();
        }
      } catch (error) {
        toastr.error('There was a problem saving');
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
      return axios({method, url, data});
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
