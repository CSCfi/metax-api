from metax_api.settings.components.access_control import Role, api_permissions, prepare_perm_values

API_TEST_USER = {"username": "testuser", "password": "testuserpassword"}
API_METAX_USER = {"username": "metax", "password": "metaxpassword"}
API_AUTH_TEST_USER = {"username": "api_auth_user", "password": "password"}

API_EXT_USER = {"username": "external", "password": "externalpassword"}

API_TEST_USERS = [API_TEST_USER, API_METAX_USER, API_AUTH_TEST_USER, API_EXT_USER]

ADDITIONAL_USER_PROJECTS_PATH = "/tmp/user_projects.json"

# represents an organizational (such as jyu) catalog in test cases
EXT_DATA_CATALOG_IDENTIFIER = "urn:nbn:fi:att:data-catalog-ext"

api_permissions.rest.apierrors.create += [Role.METAX, Role.TEST_USER]
api_permissions.rest.apierrors.read += [Role.TEST_USER]
api_permissions.rest.apierrors["update"] = [Role.METAX, Role.TEST_USER]
api_permissions.rest.apierrors.delete += [Role.TEST_USER]

api_permissions.rest.contracts.create += [Role.TEST_USER]
api_permissions.rest.contracts.read += [Role.TEST_USER]
api_permissions.rest.contracts["update"] += [Role.TEST_USER]
api_permissions.rest.contracts.delete += [Role.TEST_USER]

api_permissions.rest.datacatalogs.create += [Role.TEST_USER]
api_permissions.rest.datacatalogs["update"] += [Role.TEST_USER]
api_permissions.rest.datacatalogs.delete += [Role.TEST_USER]

api_permissions.rest.datasets.create += [Role.API_AUTH_USER, Role.EXTERNAL, Role.TEST_USER]
api_permissions.rest.datasets["update"] += [Role.API_AUTH_USER, Role.EXTERNAL, Role.TEST_USER]
api_permissions.rest.datasets.delete += [Role.API_AUTH_USER, Role.EXTERNAL, Role.TEST_USER]

api_permissions.rest.directories.read += [Role.TEST_USER]

api_permissions.rest.files.create += [Role.TEST_USER]
api_permissions.rest.files.read += [Role.TEST_USER, Role.API_AUTH_USER]
api_permissions.rest.files["update"] += [Role.TEST_USER]
api_permissions.rest.files.delete += [Role.TEST_USER]

api_permissions.rest.filestorages.create += [Role.TEST_USER]
api_permissions.rest.filestorages.read += [Role.TEST_USER]
api_permissions.rest.filestorages["update"] += [Role.TEST_USER]
api_permissions.rest.filestorages.delete += [Role.TEST_USER]

api_permissions.rpc.files.delete_project.use += [Role.TEST_USER]

API_ACCESS = prepare_perm_values(api_permissions.to_dict())