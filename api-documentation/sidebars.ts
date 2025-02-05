// @ts-check
import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    { type: "doc", id: "n2e/name-to-ethnicity-api" },
  ],
  openApiSidebar: [
    {
      type: "category",
      label: "N2E API",
      link: {
        type: "generated-index",
        title: "N2E API",
        description: "This is the official REST API documentation for www.name-to-ethnicity.com. Using our public API you can classify names into their most likely ethnicity. We do not recommend you to use the API as part of your backend or any kind of deployed service. It's mainly meant for doing experiments and to be included in, for example, your Python or R scripts.",
        slug: "/"
      },
      items: require("./docs/n2e/sidebar.js")
    }
  ]
};

export default sidebars;