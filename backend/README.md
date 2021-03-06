# USAGE

In order to set up the virtualenv, activate it and run `pip install -r requirements.txt`

## OAuth

To use OAuth, follow these steps:

**1. Install all requirements**
Activate the virtual environment and run `pip install -r requirements.txt`

**2. Run migrations for Django normally**
`python manage.py makemigrations` and `python manage.py migrate --run-syncdb`

**3. Create a superuser**
`python manage.py createsuperuser`

**4. Run the Django server**
`python manage.py runserver`

**5. Setup OAuth application**
Go to /o/applications/register/ to setup the application. The options you should use are as follows:

* **Name:** PyMarket-API
* **Client id:** Default (Note this value)
* **Client secret:** Default (Note this value)
* **Client type:** Confidential
* **Authoration grant type:** Authorization Code
* **Redirect uris:** http://127.0.0.1:8000/dummy

**6. Access the authorization endpoint**
Submit a GET request to /o/authorize/ with the following parameters:

* **response_type:** code
* **client_id:** client id you noted earlier
* **redirect_uri:** http://127.0.0.1:8000/dummy/

After authorizing the app, you will be redirected to a URL that ends in /?code= followed by a code. Note this code.

**7. Access the token endpoint**
Quickly submit a POST request to /o/token/ with the following x-www-form-urlencoded body. If you take to long, you will have to repeat step 6. The code expires fast.

* **client_id:** client id you noted earlier
* **client_secret:** client secret you noted earlier
* **code:** code from step 6
* **redirect_uri:** http://127.0.0.1:8000/dummy/
* **grant_type:** authorization_code

You should receive back an access token, a refresh token, and information about them.

**8. Use the token to access endpoints**
Submit requests to the server with a header containing `Authorization: Bearer <Your Token Here>`.

### Alternative Flow for OAuth (Simpler)

**1. Setup Django**
Follow steps 1-4 above

**2. Setup OAuth application**
Go to /o/applications/register/ to setup the application. The options are as above with one change (Redirect uris): 

* **Name:** PyMarket-API
* **Client id:** Default (Note this value)
* **Client secret:** Default (Note this value)
* **Client type:** Confidential
* **Authoration grant type:** Authorization Code
* **Redirect uris:** http://127.0.0.1:8000/authredirect/

**3. Create a .env file and add the client info**
The .env file should be located in backend/backend (same folder as wsgi.py). You might have to restart the server for it to next step to work. The file should contain the following:

```plaintext
CLIENT_ID=<Your client id>
CLIENT_SECRET=<Your client secret>
```

**4. Access the authorization endpoint**
Submit a GET request to /o/authorize/ with the following parameters:

* **response_type:** code
* **client_id:** client id you noted earlier
* **redirect_uri:** http://127.0.0.1:8000/authredirect/

This should return the token as well as all necessary information about it.

**5. Use the token to access endpoints**
Submit requests to the server with a header containing `Authorization: Bearer <Your Token Here>`.
