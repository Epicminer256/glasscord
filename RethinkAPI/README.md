# Rethink API

A python API for interfacing with Rethink

## First Time Setup

### Install dependencies

To install the dependency used, `pip install html-to-json requests`

## Using the API

### Importing into your code

If rethink.py is in the same directory as your python project, you can use `import rethink` to import the API.

### Logging in

To log into rethink, you can use the auth function which takes a username and a password as it's two arguments. 
When the funciton is executed it will return a dictionary which will contain a PHP Session ID. This will be used as the first parameter for the rest of the functions inside this API and will be refered to as a "Auth Token".

Example:

```
import rethink

rethink.url = "(YOUR URL HERE)"

auth = rethink.auth("username", "password")

print(auth)

```
returns `{'PHPSESSID': '(Your PHPSESSID here)'}`

### Error Detection

The code above is very prone to fail overtime due to the lack of error checking. I recommend wrapping all calls to the Rethink API inside a except like the example below. This will handle most of your errors

```
try:
    # Attempt using Rethink API
    # Example: auth = rethink.auth("username", "password") 
except rethink.loginIncorrectErr:
    # Handle incorrect login details exceptions (only applies to rethink.auth)
except rethink.connectionFailed:
    # Handle connection failures exceptions
except rethink.sessionAuthError:
    # Handle "Auth Token" exceptions (applies to everthing but rethink.auth and rethink.authCheck)
```

### Optimization notice

Every time a function from the Rethink API it will make a POST request. Because internet speeds are inconsistant and vary, it is best to limit the amount of requests you send.

### Getting currently enrolled classes

After logging in and getting your "Auth Token", you can now use all of the Rethink API functions. Lets list our classes.

To do so we will use rethink.getEnrolledClasses, which only takes the auth token as a argument and returns a array which contains one dict for every class.

Here is a example with error detection

```
import rethink
import json

rethink.url = "(YOUR URL HERE)"

# Log into rethink and then get our Auth Token
try:
    auth = rethink.auth("username", "password")
except rethink.loginIncorrectErr:
    print("Your username or password is incorrect")
    exit()
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()

# Get Current Classes
try:
    classes = rethink.getEnrolledClasses(auth) 
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()

# Pretty prints output
print(json.dumps(classes, indent=4))
```

Which will return this array if the login was correct and if there is a internet connection

```
[
    {
        "type": "OPEN/CLOSED",
        "classname": "CLASSNAME",
        "date": "1970-01-01",
        "room": "ROOMLOCATION",
        "openseats": "SEATSLEFT",
        "firstname": "FIRST",
        "lastname": "LAST",
        "classid": "11111"
    },
    {
        "type": "OPEN/CLOSED",
        "classname": "CLASSNAME",
        "date": "1970-01-02",
        "room": "ROOMLOCATION",
        "openseats": "SEATSLEFT",
        "firstname": "FIRST",
        "lastname": "LAST",
        "classid": "11112"
    }
]
```

This function only gets the classes for the current week (Further down the documentation there will be instructions on how to change the week)

### Getting all joinable classes

This works just like rethink.getEnrolledClasses, but gets all joinable classes instead of the ones aready chosen

Here is a example with error detection

```
import rethink
import json

rethink.url = "(YOUR URL HERE)"

# Log into rethink and then get our Auth Token
try:
    auth = rethink.auth("username", "password")
except rethink.loginIncorrectErr:
    print("Your username or password is incorrect")
    exit()
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()

# Get All Classes
try:
    classes = rethink.getAllClasses(auth)
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()

# Pretty prints output
print(json.dumps(classes, indent=4))
```

Which will return this array if the login was correct and if there is a internet connection

```
[
    {
        "type": "OPEN/CLOSED",
        "classname": "CLASSNAME",
        "date": "1970-01-01",
        "room": "ROOMLOCATION",
        "openseats": "SEATSLEFT",
        "firstname": "FIRST",
        "lastname": "LAST",
        "classid": "11111"
    },
    ... typically would be allot of classes in this list
]
```

This function only gets the classes for the current week (Next entry in the documentation there will be instructions on how to change the week)

### Shifting the week offset

Rethink selects what week is selected by offseting the real life date by a week. You can shift the week up and down by using rethink.shiftWeekUp and rethink.shiftWeekDown. Note that the week offset cannot go below zero

This function only takes the Auth Token as a argument

Using the code from the example above that was used for listing currently enrolled classes, we will modify it to show next week's classes we are in.

```
import rethink
import json

rethink.url = "(YOUR URL HERE)"

# Log into rethink and then get our Auth Token
try:
    auth = rethink.auth("username", "password")
except rethink.loginIncorrectErr:
    print("Your username or password is incorrect")
    exit()
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()

# Shift Week Up (Code we added to show next week's classes instead of the current week)
try:
    rethink.shiftWeekUp(auth)
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()

# Get Current Classes
try:
    classes = rethink.getEnrolledClasses(auth) 
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()

# Pretty prints output
print(json.dumps(classes, indent=4))
```

Which will return next week's classes

```
[
    {
        "type": "OPEN/CLOSED",
        "classname": "CLASSNAME",
        "date": "1970-01-08",
        "room": "ROOMLOCATION",
        "openseats": "SEATSLEFT",
        "firstname": "FIRST",
        "lastname": "LAST",
        "classid": "11113"
    },
	{
        "type": "OPEN/CLOSED",
        "classname": "CLASSNAME",
        "date": "1970-01-10",
        "room": "ROOMLOCATION",
        "openseats": "SEATSLEFT",
        "firstname": "FIRST",
        "lastname": "LAST",
        "classid": "11114"
    }
]
```

### Getting session info / profile info

The function rethink.getInfo only takes a Auth Token as a argument and returns the user's name, student ID, and current selected week

```
import rethink
import json

rethink.url = "(YOUR URL HERE)"

# Log into rethink and then get our Auth Token
try:
    auth = rethink.auth("username", "password")
except rethink.loginIncorrectErr:
    print("Your username or password is incorrect")
    exit()
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()

# Get session info
try:
    info = rethink.getInfo(auth) 
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()

# Pretty prints output
print(json.dumps(info, indent=4))
```

Will return this
```
{
    "name": "FIRST LAST",
    "studentid": "99999",
    "week": 0
}
```

### Adding and removing classes

To add and remove classes, use either rethink.addClass or rethink.removeClass

Both functions will take a "Auth Token" as the first argument and the second argument is a class ID

Here is a example where the user can select what class to remove
```
import rethink
import json

rethink.url = "(YOUR URL HERE)"

# Log into rethink and then get our Auth Token
try:
    auth = rethink.auth("username", "password")
except rethink.loginIncorrectErr:
    print("Your username or password is incorrect")
    exit()
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()

# Get current classes
try:
    info = rethink.getEnrolledClasses(auth) 
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()

# Pretty prints classes
print(json.dumps(info, indent=4))

# Prompts the user to select a class id to remove
print("What class do you want to remove?")
class_id = input("Class ID> ")

# Removes the selected class
try:
    rethink.removeClass(auth, class_id) 
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()
else:
    print("Removed Class")
```

And the output

```
[
    {
        "type": "OPEN/CLOSED",
        "classname": "CLASSNAME",
        "date": "1970-01-01",
        "room": "ROOMLOCATION",
        "openseats": "SEATSLEFT",
        "firstname": "FIRST",
        "lastname": "LAST",
        "classid": "11111"
    },
    {
        "type": "OPEN/CLOSED",
        "classname": "CLASSNAME",
        "date": "1970-01-02",
        "room": "ROOMLOCATION",
        "openseats": "SEATSLEFT",
        "firstname": "FIRST",
        "lastname": "LAST",
        "classid": "11112"
    }
]
What class do you want to remove?
Class ID> 11111
Removed Class
```

And for adding a class

```
import rethink
import json

rethink.url = "(YOUR URL HERE)"

# Log into rethink and then get our Auth Token
try:
    auth = rethink.auth("username", "password")
except rethink.loginIncorrectErr:
    print("Your username or password is incorrect")
    exit()
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()

# Get current classes
try:
    info = rethink.getAllClasses(auth) 
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()

# Pretty prints output
print(json.dumps(info, indent=4))

# Prompts the user to select a class id to add
print("What class do you want to add?")
class_id = input("Class ID> ")

# Adds the selected class
try:
    rethink.addClass(auth, class_id) 
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
except rethink.sessionAuthError:
    print("PHP Session Expired, try again")
    exit()
else:
    print("Added Class")
```

And the output

```
[
    {
        "type": "OPEN/CLOSED",
        "classname": "CLASSNAME",
        "date": "1970-01-01",
        "room": "ROOMLOCATION",
        "openseats": "SEATSLEFT",
        "firstname": "FIRST",
        "lastname": "LAST",
        "classid": "11111"
    },
    ... typically would be allot of classes in this list
]
What class do you want to add?
Class ID> 11111
Added Class
```

As of writing, rethink.addClass and rethink.removeClass have no detection to see if the class really got added or removed.

### Checking the Auth Token

If you optimize your code to not have the user logging in everytime, you can store the Auth Token localy instead. 

rethink.authCheck only takes the Auth Token as a parameter and returns True if the token is still logged in and False if it is logged out 

Here is a example

```
import rethink
import json
import random
import string

rethink.url = "(YOUR URL HERE)"

# Type a random string here to test if the auth check returns False
fake_auth = {
    'PHPSESSID': "".join(random.choices(string.ascii_lowercase, k=15))
}

# Log into rethink and then get our Auth Token
try:
    auth = rethink.auth("username", "password")
except rethink.loginIncorrectErr:
    print("Your username or password is incorrect")
    exit()
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()  

# Check if our logged in Auth Token is still valid
try:
    is_valid = rethink.authCheck(auth)
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
else:
    print("Our real logged in Auth Token returned "+str(is_valid))

# Check if our fake Auth Token is still valid
try:
    is_valid = rethink.authCheck(fake_auth)
except rethink.connectionFailed:
    print("Connection to Rethink's servers failed, are you connected to the internet")
    exit()
else:
    print("Our fake Auth Token returned "+str(is_valid))
```

and this outputs

```
Our real logged in Auth Token returned True
Our fake Auth Token returned False
```
