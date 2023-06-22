# coffeco-instock-analysis


# Design
Ideally, the finished product would have a user authentication page. They would be authenticated by their email and password. After authentication, they would have access to API collected data. API inventory data will be stored in a SQLite database. User authentication emails and tokens will also be stored in a separate SQLite database. The frontend dashboard will request data from the SQLite database using an authentication email and associated token. Other analysis can also be conducted on the locally stored data.
## Tooling
The frontend dashboard is a Vite typescript React project. Since it has HMR (hot module replacement), it is possible to see code changes which reflect in real-time. In order to run the Vite frontend, run the command `npm run dev` in the Vite project root.

For python package management, [poetry](https://python-poetry.org/) will be used. It can be installed with `pipx install poetry`, or any of its other recommended installations. In order to run poetry, execute `pipx run poetry <arguments>` where `<arguments>` are the CLI arguments.

Data management will be done in python. There is an Amazon SP-API wrapper available [here](https://pypi.org/project/python-amazon-sp-api/). This API wrapper has a reference available [here](https://sp-api-docs.saleweaver.com/?utm_source=github&utm_medium=repo&utm_term=badge). Since we will be analyzing inventory data, the documentation can be found [here](https://sp-api-docs.saleweaver.com/endpoints/inventories/).

Data storage can be done in SQLite. There is additionally a built-in sqlite3 library whose documentation can be found [here](https://docs.python.org/3/library/sqlite3.html#module-sqlite3)
## Data Management
### Authorization
In the database, only the user ID (integer) and user token (string) will be stored in the SQL database. The user token will be computed by a SHA256 hash of the users email and password.

Flow chart:
> User Inputs email and password. First the email and password are hashed to generate the token, then the token and email are sent to the server for authentication. If the token matches the token in the database designated to the specified email, the action will be authenticated.

Amazon SP-API authentication requires the following environment variables (API credentials documentation can be found [here](https://sp-api-docs.saleweaver.com/env_variables/)):

<div class="wy-table-responsive"><table class="docutils align-default">
<colgroup>
<col style="width: 17%">
<col style="width: 83%">
</colgroup>
<thead>
<tr class="row-odd"><th class="head"><p>ENVIRONMENT VARIABLE</p></th>
<th class="head"><p>DESCRIPTION</p></th>
</tr>
</thead>
<tbody>
<tr class="row-even"><td><p>SP_API_REFRESH_TOKEN</p></td>
<td><p>The refresh token used obtained via authorization (can be passed to the client instead)</p></td>
</tr>
<tr class="row-odd"><td><p>LWA_APP_ID</p></td>
<td><p>Your login with amazon app id</p></td>
</tr>
<tr class="row-even"><td><p>LWA_CLIENT_SECRET</p></td>
<td><p>Your login with amazon client secret</p></td>
</tr>
<tr class="row-odd"><td><p>SP_API_ACCESS_KEY</p></td>
<td><p>AWS USER ACCESS KEY</p></td>
</tr>
<tr class="row-even"><td><p>SP_API_SECRET_KEY</p></td>
<td><p>AWS USER SECRET KEY</p></td>
</tr>
<tr class="row-odd"><td><p>SP_API_ROLE_ARN (not required)</p></td>
<td><p>The role’s arn (needs permission to “Assume Role” STS) (not required)</p></td>
</tr>
</tbody>
</table></div>

### Sales Data
Sale data will also be stored in its own SQLite database. The tables of this database will be the coffee type. The columns will all contain dates and all other data that is retrieved by the SP-API call. There will be an additional option for all users to receive an email if the quantity of a product is below a threshold.

## Dashboard
The dashboard is the project frontend which contains a user login and data display. It will also contain user options. It is a Vite project. In order to run the dashboard, make sure all dependencies are installed by running `npm install`. Afterwards, run `npm run dev`.
