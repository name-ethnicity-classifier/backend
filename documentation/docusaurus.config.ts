// @ts-check

import type * as Preset from "@docusaurus/preset-classic";
import type { Config } from "@docusaurus/types";
import type * as Plugin from "@docusaurus/types/src/plugin";
import type * as OpenApiPlugin from "docusaurus-plugin-openapi-docs";

const config: Config = {
  title: "name-to-ethnicity",
  tagline: "API Documentation",
  url: "https://name-to-ethnicity.com",
  baseUrl: "/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",

  organizationName: "name-to-ethnicity",
  projectName: "name-to-ethnicity API documentation",

  presets: [
    [
      "classic",
      {
        docs: {
          routeBasePath: "/",
          sidebarPath: require.resolve("./sidebars.ts"),
          editUrl:
            "https://github.com/name-ethnicity-classifier/api-documentation/",
          docItemComponent: "@theme/ApiItem",
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig:
    {
      docs: {
        sidebar: {
          hideable: true,
        },
      },
      navbar: {
        title: "API Documentation",
        logo: {
          alt: "N2E Logo",
          src: "img/logo.svg",
        },
        items: [
          { type: "docsVersionDropdown" },
          {
            href: "https://github.com/name-ethnicity-classifier/api-documentation",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "light",
        links: [
          {
            title: "Legal",
            items: [
              {
                label: "Terms-of-Service",
                to: "https://www.name-to-ethnicity.com/terms-of-service/",
              },
              {
                label: "Privacy Policy",
                to: "https://www.name-to-ethnicity.com/privacy-policy/",
              },
            ],
          },
          {
            title: "Sites",
            items: [
              {
                label: "Visit N2E",
                href: "https://www.name-to-ethnicity.com/",
              },
              {
                label: "GitHub",
                href: "https://github.com/name-ethnicity-classifier",
              },
              {
                label: "Sponsor",
                href: "https://buymeacoffee.com/theodorpfr",
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Theodor Peifer, Inc. Built with Docusaurus.`,
      },
      prism: {
        prism: {
          additionalLanguages: [
            "python",
            "javascript",
            "json",
            "bash",
          ],
        },
        languageTabs: [
          {
            highlight: "python",
            language: "python",
            logoClass: "python",
          },
          {
            highlight: "bash",
            language: "curl",
            logoClass: "bash",
          },
          {
            highlight: "javascript",
            language: "nodejs",
            logoClass: "nodejs",
          },
          {
            highlight: "java",
            language: "java",
            logoClass: "java",
            variant: "unirest",
          },
          {
            highlight: "powershell",
            language: "powershell",
            logoClass: "powershell",
          },
        ],
      },
    } satisfies Preset.ThemeConfig,

  plugins: [
    [
      "docusaurus-plugin-openapi-docs",
      {
        id: "openapi",
        docsPluginId: "classic",
        config: {
          n2e: {
            specPath: "openapi/n2e.yaml",
            outputDir: "docs/n2e",
            sidebarOptions: {
              groupPathsBy: "tag",
              categoryLinkSource: "tag",
            },
          } satisfies OpenApiPlugin.Options,
        } satisfies Plugin.PluginOptions,
      },
    ],
  ],

  themes: ["docusaurus-theme-openapi-docs"],
};

export default async function createConfig() {
  return config;
}
