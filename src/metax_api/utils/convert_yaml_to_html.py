import logging
import json
import yaml
from os import path
from django.conf import settings

_logger = logging.getLogger(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Swagger UI</title>
  <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Source+Code+Pro:300,600|Titillium+Web:400,600,700" rel="stylesheet">
  <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui.css" >
  <style>
    html
    {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }
    *,
    *:before,
    *:after
    {
      box-sizing: inherit;
    }

    body {
      margin:0;
      background: #fafafa;
    }
  </style>
</head>
<body>

<div id="swagger-ui"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui-bundle.js"> </script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui-standalone-preset.js"> </script>
<script>
window.onload = function() {

  var spec = %s;

  // Build a system
  const ui = SwaggerUIBundle({
    spec: spec,
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout"
  })

  window.ui = ui
}
</script>
</body>

</html>
"""

FAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Swagger file creation failed</title>
</head>
<body>
    <h2>Swagger file creation failed!</h2>
</body>
</html>
"""

def yaml_to_html_convert():
    try:
        inpathv1 = path.join(settings.SWAGGER_YAML_PATH, 'v1', 'swagger.yaml')
        inpathv2 = path.join(settings.SWAGGER_YAML_PATH, 'v2', 'swagger.yaml')
        outpathv1 = path.join(settings.SWAGGER_HTML_PATH, 'v1', 'swagger.html')
        outpathv2 = path.join(settings.SWAGGER_HTML_PATH, 'v2', 'swagger.html')
        outfile1 = open(outpathv1, 'w')
        outfile2 = open(outpathv2, 'w')
        try:
            infile1 = open(inpathv1, 'r')
            spec = yaml.load(infile1, Loader=yaml.FullLoader)
            if spec.get("host") =="__METAX_ENV_DOMAIN__":
                spec["host"] = settings.SERVER_DOMAIN_NAME
            outfile1.write(TEMPLATE % json.dumps(spec))
            infile1.close()
        except FileNotFoundError:
            outfile1.write(FAIL_TEMPLATE)

        try:
            infile2 = open(inpathv2, 'r')
            spec = yaml.load(infile2, Loader=yaml.FullLoader)
            if spec.get("host") =="__METAX_ENV_DOMAIN__":
                spec["host"] = settings.SERVER_DOMAIN_NAME
            outfile2.write(TEMPLATE % json.dumps(spec))
            infile2.close()
        except FileNotFoundError:
            outfile2.write(FAIL_TEMPLATE)
        outfile1.close()
        outfile2.close()
    except yaml.YAMLError as exc:
        _logger.error("YAML loading failed")
        _logger.error(exc)
    except json.decoder.JSONDecodeError as exc:
        _logger.error("JSON loading failed")
        _logger.error(exc)
