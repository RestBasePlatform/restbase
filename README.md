# restbase

# Quickstart

## First steps

Full documentation: https://restbase-api.readthedocs.io/en/latest/

After starting the docker, you need to generate an administrator token using.

```
curl --location --request GET 'localhost:54541/GenerateAdminToken'
```

For more information about admin token: GetAdminToken Request.

After starting the container and getting the administrator token, you need to add the database using

```
curl --location --request PUT 'http://localhost:54541/Database?base_type=postgres&description=some-base&local_database_name=some_local_name&ip=SOME_IP&port=SOME_PORT&username=SOME_USER&password=SOME_PASSWORD&database=SOME_DATABASE' \
--header 'admin_token: ADMIN_TOKEN_HERE'
```

For more information about database adding visit:  AddDatabase Request

To make sure that the database is added, use

```
curl --location --request GET 'http://localhost:54541/Database/list' \
--header 'admin_token: ADMIN_TOKEN_HERE'
```

For more information about database list reuqest visit: ListDatabase Request.

After adding the database, you can check the list of all read tables use

```
curl --location --request GET 'http://localhost:54541/Table/list' \
--header 'admin_token: ADMIN_TOKEN_HERE'
```

For more information about tables list reuqest visit: Table Requests.

## Add users

To add the first user, use generate_user_token.

```
curl --location --request PUT 'localhost:54541/GenerateUserToken?token_name=TOKEN_NAME_HERE' --header 'admin_token: ADMIN_TOKEN_HERE'
```

For more information about adding a user, visit the page. GenerateUserToken Request.

To grant the user rights to retrieve data from tables use:

```
curl --location --request POST 'localhost:54541/GrantTableAccess?local_table_name=LOCAL_TABLE_NAME_HERE&user_token=USER_TOKEN_HERE' --header 'admin_token: ADMIN_TOKEN_HERE'
```

For more information about adding an access, visit the page. GrantTableAccess Request.

## Data extraction

To extract data use

```
curl --location --request GET 'http://127.0.0.1:54541/GetData?query=QUERY_HERE&local_database_name=LOCAL_DATABASE_NAME_HERE' \
   --header 'user_token: USER_TOKEN_HERE'
```

For more information about data extraction, visit the page GetData Request.
