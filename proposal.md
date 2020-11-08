# Django Unchained: T2 Project Proposal

## Part 1:

**1. What will your project do?**

Our project, PyMarket, aims to simplify business inventory management specifically optimized for small business owners. This means tailoring the experience so that vendors can set up, monitor, and adapt their business with one single tool. PyMarket is mainly focused on making the management of a store inventory more streamlined, but not the interaction between shopper and vendor. 

**2. Who will be the users?**

PyMarket will have several groups of users. Vendors will be able to perform actions such as viewing and modifying their inventories, updating stock, and setting prices. In addition, we will have admins / owners who are able to manage information for other users as well as information about the stores themselves.
Our users will register and login using their email address and password. They will also be linked with personal information (such as age, address, etc).

**How will you demo the project?**

We will demo a small React web page designed for vendors. Using the webpage, vendors will be presented with items that are in or out of stock and given the options of creating, removing, or updating inventory units that will be reflected on the client side. Although our app is focused on the backend of the store, this will give us a way of showing the functionality of our inventory management system.
In addition, we will demo an admin/owner interface where admins are able to perform CRUD operations on users as well as stores and inventories with which they are associated.


**3. What kind of data do you plan to store?**

(In our actual database, all of our different “users” will be in one user table with permissions, roles, etc.)

**User**:
* Name
* Email 
   * *We will not be needing to store the password because we will be using OAuth 2.0
* List of stores they are associated with (to be linked with stores by an unique store id)

**Store**:
* Unique Store ID
* Store Information
   * Address
   * Name
   * Category
* Items
   * Image
   * Stock of each item
   * (Optional) Price of each item
   * Description of each item
* List of users associated with the store
   * Role of each user
   * User membership (start_date)
* Roles
   * Permission of each type of user (manager, vendor, employee)




**4. What public api will you be using?**

First, we will be using OAuth for login authentication and permissions.
We will also be using a couple of Data Validation APIs to validate business and customer information:
* street address (https://www.lob.com/)
* VAT numbers for products (https://vatlayer.com/)
Also, in order to make it easier for our businesses to set up their catalog, we will be using public image api’s to get stock images for their products. (https://github.com/surhud004/Foodish#readme)


________________




## Part 2: 

1. Logistics for Small Business: As a small business owner, I want my staff and I to keep track of my store’s inventory, view purchases and history of inventory changes, and edit individual prices, quantities, and descriptions so that I can ensure my customers that I have their desired products in stock. 
* My conditions of satisfaction are
   * All employees have access to view the store’s inventory but some employees have more access than others. 
      * Ex. The ability to edit prices should only be granted to administrators like me (owner) and the manager. 
   * When I edit the price for some product, I only want the price change to affect all future purchases, not those from the past which may have had different prices.
   * If I edit the description for some item (even by 1 whitespace), then the new description should be different from the previous one. 
   * If I add/remove certain products, then I want to know when, how much, and (optional) why. All these changes should appear in my history.
      * Ex. Y units of X-product were purchased or restocked. I should be able to find and view the details.


2. Individual vs Bulk Orders:  As a holiday (tour) representative, I want my tours to be purchased in bulk (i.e. wholesale/group) so that my customers can purchase more tours at a reasonable price.  
* My conditions of satisfaction are
   * Tours can be marked for individual, bulk, or both. 
      * If both, then the price of a tour in a group order must be less than that in its individual order. 
   * A customer can only purchase a group tour if they meet the minimum quantity requirement. Meaning, if a customer wants to purchase N tours in a single, then N has to be >= the minimum quantity I defined for the tour to be considered bulk.
   * If there are X number of tours left, then any purchase (either individual or bulk) cannot surpass X. 


3. Composed Parts: As a chef, I want to know which dishes are plausible and how many I can cook given the quantity of food left in the pantry so that I don't exceed the kitchen’s limits and offer our customers dishes that cannot be made. 
* My conditions of satisfaction are
   * Clear indicators of which dishes can and cannot be made given the constraints.
   * If I want to prepare some set of plausible dishes, then I want to know the maximum number of each dish I can possibly make without breaking any constraints. 
   * Updates on pantry and dishes after every order since we cannot accurately predict how many dishes will be served on a given day. 
   * If a customer wishes to add/remove an item in a dish (ex. extra cheese, no onions), then I would like for my waiters to check if the request can be made and how it would affect the number of plausible dishes before agreeing to it. 


4. CRUD Operations: As a cashier operator at a fast-fashion store, I want to find all of last week’s merchandise, remove most of it from our online store, mark certain items for clearance, and “drop” (i.e add) this week’s merchandise so that my customers are fully aware our new and recently discounted items.  
* My conditions of satisfaction are
   * A searchable and sorting page for cashier operators to filter, find, and sort items according to some user-inputted criteria.
   * Clear indicators that items were dropped, edited (quantity and/or price), and added.
      * Dropped: The item itself should no longer appear on the webpage, but some record should be maintained for admin purposes. 
      * Edited: The item should still appear on the webpage but the price and/or quantity must be different from before. 
      * Added: New item should appear on webpage. 
________________


## Part 3:

1. Testing for the first user story (small business owner): 
* Let an employee user of a small business view the store’s inventory: pass
* Let an employee user of a small business edit an item’s price: fail
* Let an administrator of a small business edit an item’s price: pass
* Let an administrator of a small business edit an item’s price and check a past purchase price. If the price changes, fail. Else, pass.
* Let an administrator of a small business edit an item’s price and make a purchase of that item. If the price reflects the changed price, pass. Else, fail.
* Change the description of an item. Check if that change is reflected in the new description. If yes, pass. Else, fail.
* Add an amount of an item in the inventory. Check if that change and time of the change are reflected in the history. If yes, pass. Else, fail.
* Delete an amount of an item in the inventory. Check if that change and time of the change are reflected in the history. If yes, pass. Else, fail.

2. Testing for the second user story (holiday representative):
* Let a representative mark a tour as bulk (and define the minimum quantity): pass
* Let a representative mark the price of the individual tour lower than that of the bulk one: fail
* Let a customer purchase an amount of a tour marked as bulk, while the amount is lower than the minimum quantity: fail
* Let a customer purchase an amount of a tour, while the amount is larger than the amount left for that tour: fail

3. Testing for the third user story (chef):
* Let a customer request a dish or an item. Check if the app gives the correct feedback based on the stock. If yes, pass. Else, fail.
* Let a customer request a dish that the kitchen is able to offer. Check if the corresponding stock changes after the request. If yes, pass. Else, fail.
* Let a chef/waiter input a dish/single item. Check if the app gives the correct amount of this dish that the stock is able to support. If yes, pass. Else, fail.

4. Testing for CRUD Operations:
* If the user can find a page to filter, find, and sort all the items by, eg. added, price, pass. Else, fail.
* If passed the above test, check if the user can drop a bunch of items. If dropped, check if these items do not appear on the page but have a record somewhere. If yes, pass. Else, fail.
* Check if the user can edit some item. If edited, check if the item is still on the page but has different quantity/price. If yes, pass. Else, fail.
* Check if the user can add some items. If added, check if these items appeared on the page. If yes, pass. Else, fail.


________________




## Part 4:

**Framework: Django (Backend) + React (Frontend)**

Django is a Python-based web framework. React is a JavaScript library that will help us create a simple and easy-to-use frontend for our application.

**IDE: VS Code**

VS Code is a common IDE with which we are all familiar. With all of us using it, collaboration should be easy.

**Build Tool: Pynt + Virtualenv + TravisCI (Backend) npm + Parcel + Babel (Frontend)**

Pynt takes the place of a makefile and allows us to specify a set of build tasks. Virtual environments will allow us to have a greater level of control over packages. 
Travis is a CI tool that will help us confirm the success of the build and install dependencies in our virtual environment. 
npm acts as a package manager and allows us to start builds of our frontend. Parcel bundles our application. 
Babel translates modern JavaScript used by React so that legacy browsers can understand it.

**Style Checker: Black (Backend) StandardJS (Frontend)**

Black will both check and format our code to ensure that it meets their standards. 
StandardJS is easy to install and use and will take care of checking our JavaScript style.

**Unit Testing: tox + PyTest (Backend) Jest (Frontend) TravisCI**

PyTest will allow us to write unit tests for our Django code, and tox will let us specify conditions for those tests (see tox link). 
Jest is a testing framework that works well with React and Babel. We plan to run Jest and PyTest from TravisCI.

**Coverage: Coverage.Py (Backend) Jest (Frontend)**

Coverage.py is easy to use and provides detailed information about Python code coverage including lines missed. 
Jest (which is doing testing for our frontend) also supports code coverage checking for React.

**Bug Finder: Pyflakes (Backend) JSHint (Frontend)**

PyChecker will allow us to find bugs quickly and easily in our Django code. JSHint will work similarly with our React code.

**Data Store: AWS RDS free tier running PostgreSQL**

AWS RDS is easy to set up and will allow us to have a common database. PostgreSQL integrates nicely with Django and is straightforward to use.
