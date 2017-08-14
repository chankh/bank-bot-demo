# Instructions
1. Create a facebook page account, and setup a developer app. You will need the Facebook page ID and
   token for the messenger bot to work.
2. Create a CitiBank developer account, save the client ID and secret, as well as the authentication
   URL.
3. Due to limitation of *Lex*, this has to be created in `us-east-1` (North Virginia) region.
4. Use the `zip` packages for `auth-welcome`, `auth-redirect`, `citi-bot` and `facebook-webhook` to
   create the respective *Lambda* functions.
5. For `auth-redirect` and `citi-bot` functions, set environment variables `CLIENT_ID` and `CLIENT_SECRET`.
6. For `auth-welcome` function, set environment variables `PAGE_ID` and `PAGE_TOKEN`.
7. For `facebook-webhook` function, set environment variables `PAGE_ID`, `PAGE_TOKEN` and
   `CITI_AUTH_URL`.
8. Create a new API in *API Gateway* named `citi-demo`.
9. Create new resource `facebook-webhook` with `GET` and `POST` methods, linked with *Lambda*
   function `facebook-webhook`.
10. Create new resource `redirect` with `GET` method, linked with *Lambda* function `auth-redirect`.
11. For all methods, update _Integration Request_ by setting the _Body Mapping Templates_ with a
   `application/json` content type and generate a template with _Method Request passthrough_.
12. Create a table in *DynamoDB*, named `citi-demo`.
13. In the *DynamoDB* table, create a stream and trigger *Lambda* `auth-welcome`.
14. In the Facebook app page, activate messenger bot with the `facebook-webhook` URL from `API Gateway`.

# References
https://github.com/awslabs/serverless-chatbots-workshop
