import configparser

import pyperclip
import json

import requests

if __name__ == '__main__':
    addToProduction = True
    prd_acct = "uat0026@hkmpcl.com.hk"
    prd_pwd = "ABcd1234"

    clipboard_content = pyperclip.paste()
    json_data = json.loads(clipboard_content)
    cart_entries = []
    productSubtotalPrice = 0
    for store in json_data["stores"]:
        for product in store["products"]:
            cart_entries.append({"sku": product["product"]["code"], "qty": product["quantity"], "subTotalPrice": product["productSubtotalPrice"]["value"]})
            productSubtotalPrice += float(product["productSubtotalPrice"]["value"])
    #         result += product["product"]["code"] + "\t" + str(product["quantity"]) + "\r\n"
    print(cart_entries)
    print(productSubtotalPrice)

    if addToProduction:
        form_data = {"grant_type": "password", "username": prd_acct, "password": prd_pwd}
        loginRes = requests.post("https://www.hktvmall.com/hktvwebservices/oauth/token", data=form_data,
                                 headers={"Authorization": "Basic aGt0dl9pb3M6SCphSyMpSE0yNDg="})
        print(loginRes.json())
        access_token = loginRes.json()["access_token"]
        print(access_token)
        for entry in cart_entries:
            res = requests.post("https://www.hktvmall.com/hktvwebservices/v1/hktv/add_item_to_cart",
                          data={"sku": entry["sku"], "quantity": entry["qty"], "user_id": prd_acct},
                          headers={"Authorization": f"Bearer {access_token}"})
            print(entry["sku"] + " - " + str(entry["qty"]) + " - " + str(res))
            aa = 0
