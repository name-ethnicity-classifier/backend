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
    component: ComponentCreator('/', '86f'),
    routes: [
      {
        path: '/next',
        component: ComponentCreator('/next', '091'),
        routes: [
          {
            path: '/next',
            component: ComponentCreator('/next', '2cf'),
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
                path: '/next/n2e/models',
                component: ComponentCreator('/next/n2e/models', '09f'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/name-to-ethnicity-api',
                component: ComponentCreator('/next/n2e/name-to-ethnicity-api', '4be'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/next/n2e/utilities',
                component: ComponentCreator('/next/n2e/utilities', '5dc'),
                exact: true,
                sidebar: "openApiSidebar"
              }
            ]
          }
        ]
      },
      {
        path: '/',
        component: ComponentCreator('/', '5fa'),
        routes: [
          {
            path: '/',
            component: ComponentCreator('/', 'b69'),
            routes: [
              {
                path: '/n2e/classification',
                component: ComponentCreator('/n2e/classification', 'e05'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/classification-route',
                component: ComponentCreator('/n2e/classification-route', '556'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-default-models-route',
                component: ComponentCreator('/n2e/get-default-models-route', 'bfa'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-models-route',
                component: ComponentCreator('/n2e/get-models-route', 'a3b'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/get-nationalities-route',
                component: ComponentCreator('/n2e/get-nationalities-route', '72b'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/models',
                component: ComponentCreator('/n2e/models', '7b3'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/name-to-ethnicity-api',
                component: ComponentCreator('/n2e/name-to-ethnicity-api', '105'),
                exact: true,
                sidebar: "openApiSidebar"
              },
              {
                path: '/n2e/utilities',
                component: ComponentCreator('/n2e/utilities', 'e88'),
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
