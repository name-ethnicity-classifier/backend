import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebar: SidebarsConfig = {
  apisidebar: [
    {
      type: "doc",
      id: "n2e/name-to-ethnicity-api",
    },
    {
      type: "category",
      label: "Endpoints",
      link: {
        type: "doc",
        id: "n2e/endpoints",
      },
      items: [
        {
          type: "doc",
          id: "n2e/classify-names",
          label: "Classifiy names into their ethnicities",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "n2e/get-default-models",
          label: "Retrieve all of our default models",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "n2e/get-custom-models",
          label: "Retrieve all of your custom models",
          className: "api-method get",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
