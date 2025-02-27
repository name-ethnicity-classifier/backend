import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', 'de0'),
    routes: [
      {
        path: '/0.1.0',
        component: ComponentCreator('/0.1.0', '01c'),
        routes: [
          {
            path: '/0.1.0',
            component: ComponentCreator('/0.1.0', 'c2d'),
            routes: [
              {
                path: '/0.1.0/',
                component: ComponentCreator('/0.1.0/', 'cc8'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/0.1.0/n2e/classification',
                component: ComponentCreator('/0.1.0/n2e/classification', '9dd'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/0.1.0/n2e/classification-route',
                component: ComponentCreator('/0.1.0/n2e/classification-route', '667'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/0.1.0/n2e/get-default-models-route',
                component: ComponentCreator('/0.1.0/n2e/get-default-models-route', 'db1'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/0.1.0/n2e/get-models-route',
                component: ComponentCreator('/0.1.0/n2e/get-models-route', '51d'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/0.1.0/n2e/get-nationalities-route',
                component: ComponentCreator('/0.1.0/n2e/get-nationalities-route', 'ea3'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/0.1.0/n2e/miscellaneous',
                component: ComponentCreator('/0.1.0/n2e/miscellaneous', 'b37'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/0.1.0/n2e/model-management',
                component: ComponentCreator('/0.1.0/n2e/model-management', '2a6'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/0.1.0/n2e/name-to-ethnicity-api',
                component: ComponentCreator('/0.1.0/n2e/name-to-ethnicity-api', '453'),
                exact: true,
                sidebar: "openApiSidebar"
              }
            ]
          }
        ]
      },
      {
        path: '/next',
        component: ComponentCreator('/next', '478'),
        routes: [
          {
            path: '/next',
            component: ComponentCreator('/next', '81f'),
            routes: [
              {
                path: '/next/',
                component: ComponentCreator('/next/', '26c'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/classification',
                component: ComponentCreator('/next/n2e/classification', '78e'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/classification-distribution-route',
                component: ComponentCreator('/next/n2e/classification-distribution-route', 'a59'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/classification-route',
                component: ComponentCreator('/next/n2e/classification-route', '129'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/get-default-models-route',
                component: ComponentCreator('/next/n2e/get-default-models-route', '97d'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/get-models-route',
                component: ComponentCreator('/next/n2e/get-models-route', 'c03'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/get-nationalities-route',
                component: ComponentCreator('/next/n2e/get-nationalities-route', 'a0d'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/miscellaneous',
                component: ComponentCreator('/next/n2e/miscellaneous', 'af3'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/model-management',
                component: ComponentCreator('/next/n2e/model-management', 'ab4'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/name-to-ethnicity-api',
                component: ComponentCreator('/next/n2e/name-to-ethnicity-api', '4be'),
                exact: true,
                sidebar: "openApiSidebar"
              }
            ]
          }
        ]
      },
      {
        path: '/',
        component: ComponentCreator('/', '476'),
        routes: [
          {
            path: '/',
            component: ComponentCreator('/', 'f46'),
            routes: [
              {
                path: '/n2e/classification',
                component: ComponentCreator('/n2e/classification', 'f44'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/classification-distribution-route',
                component: ComponentCreator('/n2e/classification-distribution-route', '1ed'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/classification-route',
                component: ComponentCreator('/n2e/classification-route', '104'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-default-models-route',
                component: ComponentCreator('/n2e/get-default-models-route', 'ebc'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-models-route',
                component: ComponentCreator('/n2e/get-models-route', 'a1f'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-nationalities-route',
                component: ComponentCreator('/n2e/get-nationalities-route', '466'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/miscellaneous',
                component: ComponentCreator('/n2e/miscellaneous', 'ce5'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/model-management',
                component: ComponentCreator('/n2e/model-management', '5fb'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/name-to-ethnicity-api',
                component: ComponentCreator('/n2e/name-to-ethnicity-api', 'f75'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/',
                component: ComponentCreator('/', 'c94'),
                exact: true,
                sidebar: "openApiSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
