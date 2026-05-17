import type { App } from "vue";
import { Alert, Button, Drawer, Empty, Form, Input, Layout, Modal, Popconfirm, Select, Skeleton, Table, Tag } from "ant-design-vue";

const components = [Alert, Button, Drawer, Empty, Form, Input, Layout, Modal, Popconfirm, Select, Skeleton, Table, Tag];

export function installAntDesign(app: App) {
  components.forEach((component) => {
    app.use(component);
  });
}
