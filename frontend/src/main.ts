import App from '@/App.vue';

import router from '@/router';
import store, { userStore } from '@/store';
import CarbonComponentsVue from '@carbon/vue/src/index';
import axios from 'axios';
import Vue from 'vue';

Vue.use(CarbonComponentsVue);

axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';


Vue.config.productionTip = false;
Vue.config.devtools = true;


interface UserDataWrapper {
  userData: object;
}

userStore.receiveUser((window as unknown as UserDataWrapper).userData)

new Vue({
  router,
  store,
  render(h) { return h(App); },
}).$mount('#app');
