import "ant-design-vue/dist/reset.css";
import "./styles/tokens.css";

import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import { installAntDesign } from "./plugins/ant-design";
import router from "./router";

const app = createApp(App);

installAntDesign(app);

app.use(createPinia()).use(router).mount("#app");
