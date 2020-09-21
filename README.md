# Flask-RESTful-API


## Allowed HTTPs requests:
<pre>
POST    : To create resource 
PUT   : To Update resource
GET     : Get a resource or list of resources
DELETE  : To delete resource
</pre>

Must follow the steps to use the app:
1. Run app.py file and paste the corresponding server address in Postman.
2. Using /token generate a unique token. This token lasts for 3600 seconds.
3. Now paste this token in Headers field of Postman with key name as 'token' and value as the token generated.
4. Perform the relevant CRUD operations using routes defined in the below table.

<table>	
    <tr>
        <th>Route</th>
        <th>Details</th>
    </tr>
    <tr>
        <td><code>/token</code></td>
        <td>Generate a JWT token.</td>
    </tr>
    <tr>
        <td><code>/user(GET)</code></td>
        <td>Get all users.</td>
    </tr>
    <tr>
        <td><code>/user(POST)</code></td>
        <td>Add a user.</td>
    </tr>
    <tr>
        <td><code>/user/id (PUT)</code></td>
        <td>Modify an existing user having a particular id.</td>
    </tr>
    <tr>
        <td><code>/user/id (GET)</code></td>
        <td>Get a particular user.</td>
    </tr>
    <tr>
        <td><code>/user/id (DELETE)</code></td>
        <td>Delete a particular user.</td>
    </tr>
    <tr>
        <td><code>/user/term="search_term"</code></td>
        <td>Find users having username containing a particular character or term. For example. term=ashish</td>
    </tr>
</table>
<br></br>
