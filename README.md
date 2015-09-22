Easy Trunk
==========

Easy Trunk application.

Ready to be used with Heroku.

## Usage 
* Application used for outbound and inbound trunking.

### Outbound Trunk
Plivo can be used as an outbound trunk to make calls from your soft switch like FreeSWITCH or Asterisk.<br/>

* http://easytrunk.plivo.com/response/sip/route/?AUTH={auth}

Refer our [Outbound Trunk](https://www.plivo.com/docs/getting-started/outbound-trunk/) getting started document.

### Inbound Trunk
Inbound Trunking is used on numbers which have been rented on Plivo. 
All incoming calls on the Plivo numbers on your account can be forwarded to a DID, a SIP URI or an hostname.<br/>
This method is used when you want Plivo to route all incoming calls on your Plivo numbers to your soft switch.<br/>

* http://easytrunk.herokuapp.com/response/sip/inbound_trunk/?DESTINATION={Destination,FailOverDestination}

Refer our [Inbound Trunk](https://www.plivo.com/docs/getting-started/inbound-trunk/) getting started document.

### Set up Plivo Application
* Navigate to the [Application](https://manage.plivo.com/app/) page on your Plivo dashboard.
* Click on ‘Create’ to create a new application.
* Enter the appropriate URL in the ‘Answer URL’ field and set the Answer Method as GET. 