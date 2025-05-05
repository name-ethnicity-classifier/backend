[ -d ./docs/n2e ] && rm -r ./docs/n2e
cp ../openapi.json ./openapi/
cp ../openapi.yml ./openapi/
yarn docusaurus gen-api-docs all