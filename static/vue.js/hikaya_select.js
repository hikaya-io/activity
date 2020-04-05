Vue.component('ValidationProvider', VeeValidate.ValidationProvider);
Vue.component('v-select', VueSelect.VueSelect);

const template = `
<validation-provider :name="name" :ref="name" :rules="required ? 'required' : ''" v-slot="{errors}">
  <div>
      <v-select v-bind="$attrs" v-on="$listeners" @search:blur="blur(name)" 
      :class="{'hikaya-select': true, 'is-invalid': !!errors.length}">
        <template #open-indicator="{ attributes }">
          <i class="caret"></i>
        </template>
      </v-select>
      <span v-show="errors[0] && !$attrs.value" class="help is-danger">
        [[ errors[0] ]]
      </span>
  </div>
</validation-provider>
`
Vue.component('hikaya-select', {
  delimiters: ['[[', ']]'],
  template: template,
  props: {
    name: {
      type: String,
      required: true
    },
    required: Boolean
  },
  methods: {
    blur(field) {
      if (this.required) {
        const provider = this.$refs[field];
        return provider.validate();
      }
    }
  },
  watch: {
    value(val) {
      if (val) {
        console.log('passs')
      } else {
        console.log('fails')
      }
    }
  }
});
