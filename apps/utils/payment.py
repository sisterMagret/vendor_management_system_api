import json
import logging
from abc import abstractmethod

import requests


# from apps.utils.enums import InterSwitchUrl, CurrencyEnum

logger = logging.getLogger("payment")


class BasePayment:
    def __init__(self, payment):
        self.payment = (
            payment  # this indicate the instance of the payment gateway to use for the transaction
        )

    @abstractmethod
    def verify_account_number(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def verify_payment(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def transfer(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def make_payment(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def bulk_transfer(self, **kwargs) -> dict:
        pass


class PayStackHandler(BasePayment):
    """
    this method handle communicating with various payment gateways
    """

    def __init__(self, payment):
        super().__init__(payment)
        self.public_key = self.payment.public_key
        self.secret_key = self.payment.secret_key
        self.context = {}

    def get_header(self):
        return {
            "content-type": "application/json",
            "Authorization": "Bearer {}".format(self.payment.secret_key),
        }

    def get_bank(self):
        url = "https://api.paystack.co/bank"
        param = {"perPage": "100"}
        payload = requests.get(url, params=param, headers=self.get_header())
        data = json.loads(payload.content)
        # print(data['data'])
        return data

    def verify_account_number(self, **kwargs) -> dict:
        url = "https://api.paystack.co/bank/resolve"
        payload = {
            "account_number": kwargs.get("account_number"),
            "bank_code": kwargs.get("sort_code"),
        }
        try:
            payload = requests.get(url, params=payload, headers=self.get_header())
            data = json.loads(payload.content)
            if data["status"]:
                response = {
                    "status": True,
                    "account_number": data["data"]["account_number"],
                    "account_name": data["data"]["account_name"],
                    "bank_id": data["data"]["bank_id"],
                }
                return response
            else:
                response = {"status": False}
                return response
        except:
            response = {"status": False}
            return response

    def verify_payment(self, ref_id):
        url = "https://api.paystack.co/transaction/verify/{}".format(ref_id)
        self.get_header().pop("content-type")
        self.get_header().update({"Cache-Control": "no-cache"})
        counter = 1
        status = True
        context = {"status": False}
        logger.info(f"Verifying payment with ref {ref_id}")
        while status:
            payload = requests.get(url, headers=self.get_header())
            data = json.loads(payload.content)
            logger.info(f"Got data from payment {data} {ref_id}")
            if data["status"]:
                context.update(
                    {"amount": (data["data"]["amount"] / 100), "status": True, "data": data["data"]}
                )
                break
            if counter == 3:
                break
            counter = counter + 1
        return context

    def transfer(self, transfer_details: dict) -> dict:
        """
        Initiate transfer: This method should only be called after a transfer recipient has been created.
        i.e obj.create_transfer_recipient() is called
        params:
            transfer_details -> dict
                {
                "source": "balance",
                "amount": float,
                "reference": transaction.reference,
                "recipient": recipient_code (from paystack),
                "reason": str,
            }

        """
        url = f"https://api.paystack.co/transfer"
        try:

            params = {
                "source": transfer_details.get("source", "balance"),
                "amount": transfer_details.get("amount"),
                "reference": transfer_details.get("reference"),
                "recipient": transfer_details.get("recipient_code"),
                "reason": transfer_details.get("message"),
            }
            counter = 1
            status = True
            context = {"status": False}

            while status:
                response = requests.post(url, headers=self.get_header(), params=params)
                if response.json().get("status"):
                    data = response.json().get("data")
                    context.update(
                        {
                            "status": True,
                            "message": "Transfer has been queued",
                            "data": {
                                "reference": data.get("reference"),
                                "integration": data.get("integration"),
                                "domain": data.get("domain"),
                                "amount": data.get("amount"),
                                "currency": data.get("currency"),
                                "source": data.get("source"),
                                "reason": data.get("reason"),
                                "recipient": data.get("recipient"),
                                "status": data.get("status"),
                                "transfer_code": data.get("transfer_status"),
                                "id": data.get("id"),
                                "createdAt": data.get("createdAt"),
                                "updatedAt": data.get("updatedAt"),
                            },
                        }
                    )
                    break

                if counter == 3:
                    break
                counter = counter + 1
            return context

        except Exception as e:
            return f"{e}"

    def bulk_transfer(self, transfer_details: dict) -> dict:
        """
        Initiate bulk transfer to multiple accounts
        params: transfer_details
            {
            "source": "balance",
            "currency": ,
            "transfers": List[{
                "amount": 20000,
                "reason": "Life go better for you",
                "recipient": "RCP_t0ya41mp35flk40"
                }],
        """
        url = f"https://api.paystack.co/transfer/bulk"
        try:

            params = {
                "source": transfer_details.get("source", "balance"),
                "currency": transfer_details.get("currency"),
                "transfers": transfer_details.get("transfers"),
            }
            counter = 1
            status = True
            context = {"status": False}

            while status:
                response = requests.post(url, headers=self.get_header(), params=params)
                if response.json().get("status"):
                    data = response.json().get("data")
                    context.update(
                        {
                            "status": True,
                            "message": response.json().get("message"),
                            "data": data,
                        }
                    )
                    break
                if counter == 3:
                    break
                counter = counter + 1
            return context

        except Exception as e:
            return f"{e}"

    def create_transfer_recepient(self, account_details) -> dict:
        """
        Create a transfer recipient
        params: account_details -> dict
            {
                "type": "nuban",
                "name": str,
                "account_number": int,
                "bank_code": str,
                "currency": "NGN",
            }
        """
        url = f"https://api.paystack.co/transferrecipient"
        try:
            params = {
                "type": account_details.get("type", "nuban"),
                "name": account_details.get("account_name"),
                "account_number": account_details.get("account_number"),
                "bank_code": account_details.get("bank_code"),
                "currency": "NGN",
            }

            counter = 1
            status = True
            context = {"status": False}

            while status:
                response = requests.post(url, headers=self.get_header(), params=params)
                if response.json().get("status"):
                    data = response.json().get("data")
                    context.update(
                        {
                            "status": True,
                            "message": response.json().get("message"),
                            "data": {
                                "active": data.get("active"),
                                "currency": data.get("currency"),
                                "domain": data.get("domain"),
                                "id": data.get("id"),
                                "integration": data.get("integration"),
                                "name": data.get("name"),
                                "recipient_code": data.get("recipient_code"),
                                "type": data.get("type"),
                                "createdAt": data.get("createdAt"),
                                "updatedAt": data.get("updatedAt"),
                                "details": data.get("details"),
                            },
                        }
                    )
                    break
                if counter == 3:
                    break
                counter = counter + 1
            return context

        except Exception as e:
            raise f"{e}"


class RavePaymentHandler(BasePayment):
    """
    this method handle communicating with various  flutterwave payment gateways
    """

    def __init__(self, payment):
        super().__init__(payment)
        self.public_key = self.payment.public_key
        self.secret_key = self.payment.secret_key
        self.headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {self.secret_key}",
        }
        self.context = {}

    def verify_payment(self, ref_id):
        """
        This method is called when you want to verify a transaction
        params:txRef
        """
        context = {}
        url = f"https://api.flutterwave.com/v3/transactions/{ref_id}/verify"
        counter = 1
        status = True
        context = {"status": False}
        while status:
            payload = requests.get(url, headers=self.headers)
            data = json.loads(payload.content)
            if data.get("status"):
                context.update({"amount": (data["data"]["amount"]), "status": True})
                break
            if counter == 3:
                break
            counter = counter + 1
        return context

    def transfer(self, account_details: dict) -> dict:
        """
        This method is called when you want to make transfers
        params: account_details:dict -> {
            "account_number":string,
            "account_name":string (this is the recepient bank code),
            "amount":int,
            "narration":string,
            "currency":string
        }
        """
        context = {}
        url = f"https://api.flutterwave.com/v3/transfers"
        counter = 1
        status = True
        context = {"status": False}
        while status:
            payload = requests.post(url, params=account_details, headers=self.headers)
            data = json.loads(payload.content)
            if data:
                context.update({"data": (data["data"]), "status": True})
                break
            if counter == 3:
                break
            counter = counter + 1
        return context

    def bulk_transfer(self, accounts: dict) -> dict:
        """
        This method is called when you want to make bulk transfer
        :request_body: accounts:list[dict] -> {
            "title": string,
            bulk_data:[{

            "bank_code":string(this is the recepient bank code),
            "account_number":string,
            "amount":int,
            "narration":string,
            "currency":string,
            "debit_currency":string,
            "reference":string,
            "meta":[
                {
                    "first_name":string,
                    "last_name":string,
                    "email":string,
                    "mobile_number":string,
                    "recepient_address":string
                }
            ]
        },]
        }

        :SuccessResponse: {
            status: 200,
            message:"bulk transfer queued",
            data:{
                id:int,
                created_at:datatime,
                approver:"N/A"
            }
        }
        :FailedResponse: {}
        """
        context = {}
        url = f"https://api.flutterwave.com/v3/bulk-transfers"
        counter = 1
        status = True
        context = {"status": False}
        while status:
            payload = requests.post(url, params=accounts, headers=self.headers)
            data = json.loads(payload.content)
            if data:
                context.update({"data": (data["data"]), "status": True})
                break
            if counter == 3:
                break
            counter = counter + 1
        return context

    def get_bank(self):
        pass

    def verify_account_number(self, **kwargs) -> dict:
        pass


# class InterSwitchHandler(BasePayment):
#     def __init__(self, payment):
#         super().__init__(payment)
#         self.public_key = self.payment.public_key  # IKIA114A1E6F6FE9EE231776E717C6FA735021D34018
#         self.secret_key = self.payment.secret_key  # RoDBi2T8W5diZF3
#         self.headers = self.get_headers()
#         self.headers.update({
#             "accept": "application/json",
#         })
#         self.context = {}
#
#     def get_bank(self):
#         pass
#
#     def make_payment(self, **kwargs):
#         """
#         Makes a post request to interswitch to make payments
#         :request url:https://qa.interswitchng.com/api/v3/purchases
#         :action: POST
#         :url param:[
#         -amount:int,
#         -currency: str (defualt NGN),
#         -transactionRef:required Transaction Reference or identifier. Each and every transaction must have an identifier must be unique (max 15 characters) generated on our system string
#         -customerId: customer id,
#         -authData: Combination of the sensitive data of the payment (PAN, PIN, Expiry Date, and CVV2)
#         ]
#         """
#         try:
#             context = {}
#             url = "https://qa.interswitchng.com/api/v3/purchases"
#
#             params =  {
#                 "customerId": kwargs.get("customerId"),
#                 "amount": kwargs.get("amount"),
#                 "transactionRef": kwargs.get("transactionReference"),
#                 "currency": self.kwargs.get("currency", "NGN"),
#                 "authData": self.kwargs.get("authData")
#             }
#
#             counter = 1
#             status = True
#
#             while status:
#                 response = requests.post(url, params=params)
#                 data = response.json()
#
#                 if data:
#                     if data.get("ResponseCode") == 00:
#                         #update context
#                         context.update({"data": data})
#                         break
#
#                 if counter == 3:
#                     break
#                 counter = counter + 1
#             return context
#
#         except Exception as e:
#             return f"{e}"
#
#     def verify_payment(self, **kwargs):
#         """
#         interswitch verify payment method
#         :param productCode: merchant product identifier.
#         :param transcationReference: Original transaction reference sent in the original request (transaction reference you generated for this)
#         """
#         context = {}
#         url = f"https://qa.interswitchng.com/collections/api/v1/gettransaction.json"
#         counter = 1
#         status = True
#         context = {"status": False}
#         params = {
#             "merchantCode": kwargs.get("merchantCode"),
#             "transactionReference": kwargs.get("transactionReference"),
#         }
#         while status:
#             payload = requests.get(url, params=params, headers=self.headers)
#             data = json.loads(payload.content)
#
#             if data:
#                 if data.get("ResponseCode") == "00":
#                     context.update({"data": data, "status": True, "amount": data.get("amount")})
#                     break
#                 context.update({"data": data})
#                 break
#
#             if counter == 3:
#                 break
#             counter = counter + 1
#         return context
#
#     def verify_account_number(self, ref):
#         return {}
#
#     def generate_access_token(self):
#         """
#         method handle generate access token to be use for quick-teller requests
#         """
#         context = {"status": True}
#         try:
#             if self.payment.is_credential_valid is False:
#                 raise ValidationError("Quick teller credentials not valid")
#             tokens = f"{self.payment.public_key}:{self.payment.secret_key}"
#             encoded_u = base64.b64encode(tokens.encode()).decode()
#             headers = {
#                 "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
#                 "Authorization": "Basic %s" % encoded_u,
#             }
#             post_data = f"grant_type=client_credentials"
#             response = requests.post(
#                 InterSwitchUrl.OBTAIN_ACCESS_TOKEN, data=post_data, headers=headers
#             )
#             data = response.json()
#             if response.status_code == status.HTTP_200_OK:
#                 payload = {
#                     "qa_access_token": data.get("access_token"),
#                     "qa_expires_in": make_aware(
#                         datetime.today() + timedelta(hours=int(data.get("expires_in")) // 3600),
#                         timezone=pytz.timezone("Africa/Lagos"),
#                     ),
#                     # expires_in comes in seconds so we need to convert it to hours
#                     "qa_scope": data.get("scope"),
#                     "qa_merchant_code": data.get("merchant_code"),
#                     "qa_payable_id": data.get("payable_id"),
#                     "qa_jti": data.get("jti"),
#                 }
#                 for key, value in payload.items():
#                     setattr(self.payment, key, value)
#                 self.payment.save()
#             else:
#                 logger.error(f"Obtaining quick-teller access token not successful due to {data}")
#                 context.update({"status": False})
#         except Exception as ex:
#             logger.error(f"Obtaining quick-teller access token not successful due to {str(ex)}")
#             logger.error(format_exc(ex))
#             context.update({"status": False})
#         return context


class PaymentHandler:
    def __init__(self, client):
        self.client = client

    def verify_account_number(self, *args, **kwargs):
        return self.client.verify_account_number(**kwargs)

    def verify_payment(self, *args, **kwargs):
        return self.client.verify_payment(**kwargs)

    def __can_execute(self, method):
        """
        this method check both the data source class and inject object if the supplied method can be executed or not
        """
        method_list = [_method for _method in dir(self.client) if _method.startswith("__") is False]
        source_method = [_method for _method in dir(self) if _method.startswith("__") is False]
        if method not in method_list or method not in source_method:
            raise NotImplementedError("Method not implemented")
        return method in method_list

    def run(self, method, *args, **kwargs):
        """
        The method run the appropriated method after validating if the method exist
        """
        if self.__can_execute(method):
            func = getattr(self, method)
            if kwargs.get("ref_id"):
                return func(element_id=kwargs.get("element_id"))
            return func(self, *args, **kwargs)
