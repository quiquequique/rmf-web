# Description

This project is about a server that exposes two APIs, one for writing logs to a persistent storage and the other for generating reports. As the project's name says, the idea is to work as a reporting server. The reporting server is designed to receive data through [Fluentd](https://www.fluentd.org/) (a data collection tool) from different pods within a Kubernetes cluster. Log data is transformed via a parser from the format that Fluentd uses for storage in the server. You can find the log formats [here](https://github.com/open-rmf/rmf-web/blob/main/packages/reporting-server/rest_server/__mocks__/raw_data.py).

In the following image, we can observe how all the pods interact with the reporting server
![rmf-web kubernetes cluster diagram](https://user-images.githubusercontent.com/28668944/123916706-8b56e300-d9b4-11eb-990f-69e717f87b38.png)


# Setup

Install pipenv

```bash
pip3 install pipenv
```

If not already done so, [bootstrap](../../README.md#bootstrap) the project, you can use

```bash
scripts/bootstrap.sh reporting-server
```

to bootstrap only this package.

# Run the server

```bash
reporting_server
```

When you run this command, two instances of the reporting server will run. One on port 8002 where the endpoints will be enabled to ask for reports and 8003 where the endpoints will be enabled to send logs to the reporting server.

![image](https://user-images.githubusercontent.com/11761240/123881439-b12bab80-d912-11eb-987a-77591add6c5d.png)

For development we recommend running this command:

```bash
uvicorn --reload rest_server.app:get_app
```

This would only create one instance of the reporting-server and it'll serve on the default port.

## Configuration

Config files are python modules that export a variable named `config`. See [default_config.py](rest_server/default_config.py) for an example and list of the options available. All options are REQUIRED unless specified otherwise.

Configuration is read from the file specified in the env `RMF_REPORT_REST_SERVER_CONFIG`, if not provided, the default config is used.

e.g.
```bash
RMF_REPORT_REST_SERVER_CONFIG='my_config.py' reporting_server
```


## Supported databases

`reporting-server` uses [tortoise-orm](https://github.com/tortoise/tortoise-orm/) to perform database operations. Currently, the supported databases are

* PostgreSQL
* SQLite
* MySQL
* MariaDB

by default it uses a in-memory sqlite instance, to use other databases, install rmf-server with the relevalent extras

* PostgreSQL - postgres
* MySQL - mysql
* MariaDB - maria

.e.g.

```bash
pip3 install reporting-server[postgres]
```

Then in your config, set the `db_url` accordingly, the url should be in the form

```
DB_TYPE://USERNAME:PASSWORD@HOST:PORT/DB_NAME?PARAM1=value&PARAM2=value
```

for example, to connect to postgres

```
postgres://<user>:<password>@<host>/<database>
```

for more information, see https://tortoise-orm.readthedocs.io/en/latest/databases.html.


# Developers

## Running tests

### Running unit tests

```bash
npm run test
```

### Collecting code coverage

```bash
npm run test:cov
```

Generate coverage report
```bash
npm run test:report
```

## Live reload

```bash
uvicorn --reload rest_server.app:get_app
```

## QA

*  I have a zombie process running either on port 8002 or 8003?

   The `reporting_server` runs two instances of the app on the same process. So, sometimes when you shut down one of the reporting-server instances, the other stay alive, resulting in a zombie process. You can kill it by running this command `kill -9 <process id>` (on Linux based OS). That's why we recommend using `uvicorn --reload rest_server.app:get_app` for development purposes.
