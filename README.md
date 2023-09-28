# TCG market simulator
_TCG market API application in Python (training project)_
[_Go check it out HERE!_](https://tcg-lasko-laskov.onrender.com/)

## How to use

Go at `Authenticate` tab and use the endpoints there to create your new user and get your access token.
Then click the `Authorize` button at the top-rigth(below the title), paste your token and click `Authorize` then `Close`.
Conrgratz! You are now authorized automaticaly for all requests done from this UI 😀.

Upon registering new user, you will receive 5 new cards for you collection (and some credits 😉)!
The cards are loaded from this awesome _Magic The Gathering_  (if you dont't know what this is, you are missing out) API:
https://docs.magicthegathering.io/

You can go check the `My Data` endpoints to see details about your user and card colection.
Use the `Market` endpoints, to check the currently available cards on the market, make your cards available to sell and buy cards from other users.
Finaly if your user is _ADMIN_, you can utilize the `Admin` endpoints, to buy and sell cards on behalf of other users, as well as see full information about all users and all cards loaded in the database.

Bellow you can see a short description of all endpoints:

#### Authenticate

| URL | Description |
| ------ | ------ |
| `/auth` | Get you access token by providing your `username` and `password`. |
| `/signup` | Create a new user for you. You can use dummy e-mails, there is no verification.  |

#### My Data

| URL | Description |
| ------ | ------ |
| `/my/user` | See datails about your user, including your available credits. |
| `/my/collection` | Check out your awsome collection. |

#### Market

| URL | Description |
| ------ | ------ |
| `/market` | Check out all cards available for sell and their prices. |
| `/sell` | Marks one of your cards available for sell, for a specified price. |
| `/buy` | Buy card that is available on the market. You must have sufficient credits to make it happen! |
| `/cancel` | Pull one of your cards off the market.  |

#### Admin

| URL | Description |
| ------ | ------ |
| `/admin/sell` | Mark any card, owned by any user available for sell. |
| `/admin/buy` | Buy a card on the markt on behalf of any user. Still the user needs to have the credits.  |
| `/admin/cancel` | Pull any card off the market. |
| `/admin/users` | See info about all users.  |
| `/admin/cards` | See all cards currently loaded in the database. |

