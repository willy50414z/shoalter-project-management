import pyperclip
import json

def removeEmptyList(json, key):
    if key in json and isinstance(json[key], list) and len(json[key]) == 0:
        json.pop(key)
    return json

def removeEmptyStr(json, key):
    if key in json and isinstance(json[key], str) and json[key] == "":
        json.pop(key)
    return json


def removeKeyIfExist(json, key):
    if key in json:
        json.pop(key)
    return json

def sortKey(json):
    sorted_keys = sorted(json.keys())
    sorted_data_dict = {}
    for key in sorted_keys:
        if isinstance(json[key], dict):
            json[key] = sortKey(json[key])
        if isinstance(json[key], list):
            for i in range(len(json[key])):
                if isinstance(json[key][i], dict) or isinstance(json[key][i], list):
                    json[key][i] = sortKey(json[key][i])

        sorted_data_dict[key] = json[key]
    return sorted_data_dict

def sort_store_product(json_data):
    sorted_items = sorted(json_data["stores"][0]["products"],
                          key=lambda x: x["product"]["baseOptions"][0]["selected"]["code"])
    json_data["stores"][0]["products"] = sorted_items

def sort_freegift(json_data):
    sorted_items = sorted(json_data["freeGifts"],
                          key=lambda x: x["orderEntries"][0]["product"]["code"])
    json_data["freeGifts"] = sorted_items

def remove_empty_list(json_data):
    if "stores" in json_data and len(json_data["stores"]) > 0:
        # sort by product code
        sort_store_product(json_data)

        # null to empty
        for product in json_data["stores"][0]["products"]:
            removeEmptyList(product["product"]["baseOptions"][0], "options")
            removeEmptyList(product["product"]["baseOptions"][0]["selected"], "labels")
            removeEmptyList(product["product"]["baseOptions"][0]["selected"], "potentialPromotions")
            removeEmptyList(product["product"]["baseOptions"][0]["selected"], "priceList")
            removeEmptyList(product["product"]["baseOptions"][0]["selected"], "recommendedSellingPrice")
            removeEmptyList(product["product"]["baseOptions"][0]["selected"], "savedPrice")
            removeEmptyList(product["product"], "overseasRegionCodes")
            removeEmptyList(product["product"], "storeTags")
            removeEmptyList(product["product"], "deliveryLabelScheduleCode")
            removeEmptyList(product["product"], "images")

    if "freeGifts" in json_data and len(json_data["freeGifts"]) > 0:
        for freeGift in json_data["freeGifts"]:
            for orderEntry in freeGift["orderEntries"]:
                removeEmptyList(orderEntry["product"], "baseOptions")
                removeEmptyList(orderEntry["product"], "bundlePromotionList")
                removeEmptyList(orderEntry["product"], "categories")
                removeEmptyList(orderEntry["product"], "categoryLevelRecommendation")
                removeEmptyList(orderEntry["product"], "classifications")
                removeEmptyList(orderEntry["product"], "colors")
                removeEmptyList(orderEntry["product"], "completeTheLook")
                removeEmptyList(orderEntry["product"], "deliverableRegions")
                removeEmptyList(orderEntry["product"], "firstCategoryNameList")
                removeEmptyList(orderEntry["product"], "fixedDeliveryTimeSlot")
                removeEmptyList(orderEntry["product"], "futureStocks")
                removeEmptyList(orderEntry["product"], "genders")
                removeEmptyList(orderEntry["product"], "imageUrls")
                removeEmptyList(orderEntry["product"], "keywords")
                removeEmptyList(orderEntry["product"], "labels")
                removeEmptyList(orderEntry["product"], "marketingLabelUids")
                removeEmptyList(orderEntry["product"], "marketingLabels")
                removeEmptyList(orderEntry["product"], "membershipLoyaltyPoint")
                removeEmptyList(orderEntry["product"], "overseasRegionCodes")
                removeEmptyList(orderEntry["product"], "perfectPartnerPromotionList")
                removeEmptyList(orderEntry["product"], "photosTabImages")
                removeEmptyList(orderEntry["product"], "pickLabelList")
                removeEmptyList(orderEntry["product"], "pickLabelUids")
                removeEmptyList(orderEntry["product"], "potentialPromotions")
                removeEmptyList(orderEntry["product"], "previewLabels")
                removeEmptyList(orderEntry["product"], "previewPriceList")
                removeEmptyList(orderEntry["product"], "priceList")
                removeEmptyList(orderEntry["product"], "productReferences")
                removeEmptyList(orderEntry["product"], "promotionBanners")
                removeEmptyList(orderEntry["product"], "recommendation")
                removeEmptyList(orderEntry["product"], "reviews")
                removeEmptyList(orderEntry["product"], "savedPrice")
                removeEmptyList(orderEntry["product"], "skuLevelRecommendation")
                removeEmptyList(orderEntry["product"], "storeTags")
                removeEmptyList(orderEntry["product"], "subCatRecommendation")
                removeEmptyList(orderEntry["product"], "tags")
                removeEmptyList(orderEntry["product"], "thresholdPromotionList")
                removeEmptyList(orderEntry["product"], "variantMatrix")
                removeEmptyList(orderEntry["product"], "variantOptions")
                removeEmptyList(orderEntry["product"], "volumePrices")

    if "thresholdPromotionDetails" in json_data:
        for thresholdPromotionDetails in json_data["thresholdPromotionDetails"]:
            removeEmptyList(thresholdPromotionDetails, "giveAwayCouponCodes")

def remove_empty_srting(json_data):
    for thresholdPromotionDetail in json_data["thresholdPromotionDetails"]:
        for consumedEntry in thresholdPromotionDetail["consumedEntries"]:
            removeEmptyStr(consumedEntry, "name")

def remove_new_fields(json_data):
    if "stores" in json_data and len(json_data["stores"]) > 0:
        removeKeyIfExist(json_data["stores"][0], "isHKTVBatch")
        for product in json_data["stores"][0]["products"]:
            removeKeyIfExist(product["product"]["baseOptions"][0]["selected"]["stock"], "mainlandWarehouse")
            removeKeyIfExist(product["product"]["baseOptions"][0]["selected"]["stock"], "warehouseCode")
            removeKeyIfExist(product["product"], "extendedWarrantyProductList")
            removeKeyIfExist(product["product"], "mainlandWarehouse")
            removeKeyIfExist(product["product"], "pricePercentage")
            removeKeyIfExist(product, "deliveryLabelCodeInSchedule")
            removeKeyIfExist(product["product"]["stock"], "mainlandWarehouse")
            removeKeyIfExist(product["product"]["stock"], "warehouseCode")
            if "deliveryLabelScheduleCode" in product["product"] and len(product["product"]["deliveryLabelScheduleCode"]) > 0:
                for deliveryLabelScheduleCode in product["product"]["deliveryLabelScheduleCode"]:
                    removeKeyIfExist(deliveryLabelScheduleCode, "earliestDeliveryTimestamp")
    if "productOutOfStock" in json_data and "deliveryLabelScheduleCode" in json_data["productOutOfStock"] and len(json_data["productOutOfStock"]["deliveryLabelScheduleCode"]) > 0:
        for deliveryLabelScheduleCode in json_data["productOutOfStock"]["deliveryLabelScheduleCode"]:
            removeKeyIfExist(deliveryLabelScheduleCode, "earliestDeliveryTimestamp")


    if "freeGifts" in json_data and len(json_data["freeGifts"]) > 0:
        for freeGift in json_data["freeGifts"]:
            for orderEntry in freeGift["orderEntries"]:
                removeKeyIfExist(orderEntry["product"], "mainlandWarehouse")
                removeKeyIfExist(orderEntry["product"], "pricePercentage")

if __name__ == '__main__':
    # 读取剪贴板内容
    clipboard_content = pyperclip.paste()
    json_data = json.loads(clipboard_content)

    sort_store_product(json_data)
    sort_freegift(json_data)

    remove_empty_list(json_data)
    remove_empty_srting(json_data)
    remove_new_fields(json_data)

    #sort key
    json_data = sortKey(json_data)

    output_json = json.dumps(json_data, ensure_ascii=False, indent=4)
    # print(output_json)
    pyperclip.copy(output_json)
