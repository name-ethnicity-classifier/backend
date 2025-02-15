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
    component: ComponentCreator('/', 'f1d'),
    routes: [
      {
        path: '/next',
        component: ComponentCreator('/next', '51c'),
        routes: [
          {
            path: '/next',
            component: ComponentCreator('/next', '3a6'),
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
        component: ComponentCreator('/', '56b'),
        routes: [
          {
            path: '/',
            component: ComponentCreator('/', '853'),
            routes: [
              {
                path: '/n2e/classification',
                component: ComponentCreator('/n2e/classification', '538'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/classification-route',
                component: ComponentCreator('/n2e/classification-route', '048'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-default-models-route',
                component: ComponentCreator('/n2e/get-default-models-route', '6f2'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-models-route',
                component: ComponentCreator('/n2e/get-models-route', '4bc'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-nationalities-route',
                component: ComponentCreator('/n2e/get-nationalities-route', '7e8'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/miscellaneous',
                component: ComponentCreator('/n2e/miscellaneous', 'c46'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/model-management',
                component: ComponentCreator('/n2e/model-management', '79a'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/name-to-ethnicity-api',
                component: ComponentCreator('/n2e/name-to-ethnicity-api', '5a0'),
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
