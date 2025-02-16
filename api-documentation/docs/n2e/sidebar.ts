import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebar: SidebarsConfig = {
  apisidebar: [
    {
      type: "doc",
      id: "n2e/name-to-ethnicity-api",
    },
    {
      type: "category",
      label: "Classification",
      link: {
        type: "doc",
        id: "n2e/classification",
      },
      items: [
        {
          type: "doc",
          id: "n2e/classification-route",
          label: "Classify names.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Model Management",
      link: {
        type: "doc",
        id: "n2e/model-management",
      },
      items: [
        {
          type: "doc",
          id: "n2e/get-models-route",
          label: "Get all models.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "n2e/get-default-models-route",
          label: "Get all default models.",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Miscellaneous",
      link: {
        type: "doc",
        id: "n2e/miscellaneous",
      },
      items: [
        {
          type: "doc",
          id: "n2e/get-nationalities-route",
          label: "Returns a list of all available nationalities (49) and nat. groups (8) along with the amount of samples we have of them in our dataset.",
          className: "api-method get",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
