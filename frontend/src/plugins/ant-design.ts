import type { App } from "vue";
import { Alert, Button, Form, Input, Layout, Tag } from "ant-design-vue";

const components = [Alert, Button, Form, Input, Layout, Tag];

export function installAntDesign(app: App) {
  components.forEach((component) => {
    app.use(component);
  });
}
