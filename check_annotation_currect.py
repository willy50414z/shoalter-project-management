import os
import re
import shutil
import time
from service import java_parse_svc

base_dir = "E:/Code/shoalter-ecommerce-business/shoalter-ecommerce-business-"


def get_has_ann_file():
    start_time = time.time()
    root_dir = 'C:/work/hybris_docker/hybris_docker_hktvmall/bin/'
    target_root_dir = 'C:/work/hybris_src_code_migration_annotation/bin/'

    # Pattern to search for
    pattern = re.compile(r'@EcomRevamp')

    # List to store the files that contain the pattern
    matching_files = []

    # Walk through the directory
    for subdir, _, files in os.walk(root_dir):
        # skip committable dir
        # if subdir.startswith("C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv-dob") or subdir.startswith(
        #         "C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv-oms") or subdir.startswith(
        #     "C:/work/hybris_docker/hybris_docker_hktvmall/bin/resources") or subdir.startswith(
        #     "C:/work/hybris_docker/hybris_docker_hktvmall/bin/cis") or subdir.startswith(
        #     "C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv") or subdir.startswith(
        #     "C:/work/hybris_docker/hybris_docker_hktvmall/bin/tools"):
        #     continue

        for source_file in files:
            # Check if the file is a .java file
            if source_file.endswith('.java'):
                file_path = os.path.join(subdir, source_file)
                # Open and read the file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents = f.read()
                        # Search for the pattern
                        if pattern.search(contents):
                            matching_files.append(file_path)
                except FileNotFoundError:
                    print(f"{file_path} can't be read")
    return matching_files


def get_method_paths(matching_files):
    anno_infos = java_parse_svc.get_revamp_file_anno_info(matching_files)
    method_path_list = []
    for anno_info in anno_infos:
        if "methodPath" in anno_info:
            method_path_list.extend(anno_info["methodPath"])
    return method_path_list


def check_method_exist(methodPath):
    methodPathAr = methodPath.split("#")
    if len(methodPathAr) < 3:
        return
    service = methodPathAr[0]
    clazzName = methodPathAr[1]
    methodName = methodPathAr[2]
    if "getConsignmentWarehouseAndThirdPartyLogisticsWarehouseOrderEntries" == methodName:
        aa = 1
    methodExist = False
    fileExist = False
    if service == "cart-service" and not clazzName.endswith("Repository"):
        for subdir, _, files in os.walk(base_dir + service):
            for file in files:
                if file.endswith(clazzName + ".java"):
                    fileExist = True
                    if "getConsignmentWarehouseAndThirdPartyLogisticsWarehouseOrderEntries" == methodName:
                        aa = 1
                    file_path = os.path.join(subdir, file)
                    java_structure = java_parse_svc.get_java_file_info(file_path)
                    method_list = java_structure[""]
                    for method in method_list:
                        if method.name == methodName:
                            methodExist = True

        # if not fileExist:
        #     print(f"file not exist[{clazzName}]")
        if not methodExist:
            print(f"method not exist[{methodPath}]")
        # else:
        #     print(f"{methodPath} exist")


if __name__ == '__main__':
    # matching_files = get_has_ann_file()
    matching_files = [
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/address/converters/populator/SingleLineAddressFormatPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/order/converters/populator/AbstractDeliveryModePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/order/converters/populator/AbstractOrderPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/order/converters/populator/CartModificationPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/order/converters/populator/CartPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/order/converters/populator/DeliveryModePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/order/converters/populator/OrderEntryPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/order/converters/populator/PromotionResultPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/order/impl/DefaultCartFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/CategoryPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/CategoryUrlPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/ImagePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/ProductPricePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/ProductPrimaryImagePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/ProductPromotionsPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/ProductStockPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/ProductUrlPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/PromotionsPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/converters/populator/VariantSelectedPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/impl/DefaultPriceDataFactory.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/impl/DefaultProductFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/product/impl/DefaultProductVariantFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/user/converters/populator/AddressPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/user/impl/DefaultUserFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commercefacades/src/de/hybris/platform/commercefacades/voucher/converters/populator/OrderAppliedVouchersPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commerceservices/src/de/hybris/platform/commerceservices/customer/impl/DefaultCustomerAccountService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commerceservices/src/de/hybris/platform/commerceservices/order/impl/DefaultCommerceCartCalculationStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commerceservices/src/de/hybris/platform/commerceservices/order/impl/DefaultCommerceCartService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commerceservices/src/de/hybris/platform/commerceservices/stock/strategies/impl/DefaultCommerceAvailabilityCalculationStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-commerce/commerceservices/src/de/hybris/platform/commerceservices/strategies/impl/DefaultCartValidationStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcheckoutaddon/acceleratoraddon/web/src/hk/com/hktv/controllers/ajax/SingleStepCheckoutAjaxController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcheckoutaddon/acceleratoraddon/web/src/hk/com/hktv/controllers/pages/checkout/steps/ExpressCheckoutController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcheckoutaddon/acceleratoraddon/web/src/hk/com/hktv/controllers/pages/checkout/steps/SingleStepCheckoutController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/core/constants/service/impl/DefaultSystemVariableService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/core/helper/HktvCalculationHelper.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/integration/cis/payment/impl/DefaultHktvCitibankCobrandPaymentService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/integration/cis/payment/impl/DefaultHktvPaymentService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/integration/cis/payment/impl/DefaultHktvPaymentSwitchService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/integration/cis/payment/impl/DefaultHktvPaymePaymentService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/integration/cis/payment/impl/DefaultHktvPaypalPaymentService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/integration/cis/payment/impl/PayDollarCisPaymentService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/integration/cis/payment/impl/PosCisPaymentService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcispayment/src/hk/com/hktv/integration/cis/payment/utils/PswRestfulUtilService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/bannerContainer/dao/impl/DefaultHktvBannerContainerDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/bannerContainer/service/impl/DefaultHktvBannerContainerService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/businesslogic/dao/impl/DefaultHktvCTMDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/businesslogic/dao/impl/DefaultMFoodDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cache/impl/DefaultHktvMessageUnreadCountCacheService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cache/impl/DefaultHktvPageCategoryTreeCacheService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cart/dao/impl/HktvShoppingCartDaoImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cart/service/impl/DefaultHktvCartService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cart/service/impl/DefaultHktvCommerceCartService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cart/service/impl/HktvShoppingCartServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cart/service/strategy/DefaultHktvCommerceAddToCartStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cms/service/impl/DefaultHKTVCMSItemResolverService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cmsComponent/dao/impl/DefaultHktvCmsComponentDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/cmsComponent/service/impl/DefaultHktvCmsComponentService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/commission/service/impl/CommissionServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/comms/service/impl/DefaultHktvUcApiReviewStatService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/customer/dao/impl/DefaultHktvCustomerAdvertisingDaoImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/customer/dao/impl/DefaultHktvCustomerDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/customer/impl/DefaultHktvCustomerAdvertisingServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/customer/impl/HktvCustomerAccountServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/deliveryFee/service/impl/HktvDeliveryFeeServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/gcrs/facade/impl/DefaultHktvGcrsFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/hotSearchKeyWordsComponent/service/impl/DefaultHktvHotSearchKeyWordsService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/media/url/impl/HktvLocalMediaWebURLStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/product/dao/impl/DefaultHktvProductDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/product/dao/impl/DefaultHktvProductMarketingCampaignDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/product/service/impl/DefaultHktvProductMarketingCampaignService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/product/service/impl/DefaultHktvProductService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotion/dao/impl/DefaultHktvBuyMoreSaveMorePromotionDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotion/dao/impl/DefaultHktvPromotionDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotion/service/impl/DefaultHktvBuyMoreSaveMorePromotionService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotion/service/impl/DefaultHktvPromotionService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/CreditApplyPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvBundleDiscountToFixedAmtPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvMarketingCampaignRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvOrderLevelFreeGiftPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPaymentInfoDeductCentsPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvProductBuyMoreSaveMorePromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvProductPercentageDiscountPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvProductThresholdLevelFreeGiftPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvProductThresholdLevelPerfectPartnerMerchantPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvProductThresholdLevelPerfectPartnerPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvProductThresholdPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionAddressRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionBilledAmountRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionCampaignCodeRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionDeliveryModeRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionNewCustomerRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionOrderAddFreeGiftAction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionPaymentRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionPhone1FirstOrderRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionUserAndDateRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/HktvPromotionUserFirstOrderRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/MerchantPromotionOrderEntryAdjustAction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/OrderStoreThresholdChangeDeliveryModePromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/OrderThresholdPercentageDiscountPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/ProductThresholdLevelFixedAmtDiscountMerchantPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/ProductThresholdLevelFixedAmtDiscountPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/ProductThresholdLevelPercentDiscountMerchantPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/ProductThresholdLevelPercentDiscountPromotion.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/PromotionCreditAction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/PromotionMerchantDeliveryFeeAction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/promotions/jalo/PromotionOrderStoreChangeDeliveryCostAction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/purchasedItems/service/impl/DefaultHktvPurchasedItemsService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/social/impl/DefaultHktvSalesChannelService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/urlresolver/impl/DefaultHktvProductModelUrlResolver.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/urlresolver/impl/DefaultStoreModelUrlResolver.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/urlresolver/impl/HktvCategoryModelUrlResolver.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/user/impl/HktvUserService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/wishlist/dao/impl/DefaultHktvMyListDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/wishlist/service/impl/DefaultHktvMyListServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/core/zone/impl/DefaultHktvZoneService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvcore/src/hk/com/hktv/strategy/cart/HktvCartValidationStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/category/impl/DefaultHktvCategoryFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/credit/impl/DefaultHktvCreditFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/customer/HktvCustomerFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/delivery/impl/DefaultHktvDeliveryUnitFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/ecoupon/impl/DefaultHktvECouponFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/elderly/impl/DefaultHktvElderlyFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/hktvproduct/impl/DefaultHktvProductfacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/hotSearchKeyWordsComponent/impl/DefaultHktvHotSearchKeyWordsFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/logo/impl/DefaultLogoFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/notifyme/impl/DefaultHktvNotifyMeFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/order/impl/DefaultHktvCheckoutFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/order/impl/DefaultHktvOrderFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/pickLabel/impl/DefaultHktvPickLabelFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/AcceleratorVariantOptionDataPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvBaseOptionDataPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvCartAddTotalPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvCartEntryProductPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvCartGiftProductPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvCartModificationPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvCartTotalPricePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvCustomerPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvDeliveryRemarksUIValidationPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvMembershipLevelLoyaltyPointPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductAverageRatingPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductBaseProductPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductBrandPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductCategoriesPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductColorPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductCountryOfOriginPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductDeliveryPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductEcouponPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductExtendedWarrantyProuductListPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductInvisiblePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductManufacturerPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductMediaPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductNamePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductNotifyMePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductNumberOfReviewsPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductNumberOfVariantsPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductOverseasDeliveryLabelCodesPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPackingSpecPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPickLabelDataPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPickUpReturnPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPricePercentagePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPriceUpdatedDatePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPrimaryCategoryCodePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPrimaryImagePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPromotionsPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPromotionTextPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPurchasablePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductPurchaseOptionPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductRecommendedPricePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductSalesNumberPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductStorePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductSummaryPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductUserMaxPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductVariantTypePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductWeeePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvProductZonePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvPromotionOrderEntryConsumedPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/HktvStockPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/StorePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/populators/StoreWSPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/product/impl/DefaultHktvPriceDataFactory.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/product/impl/DefaultHktvProductSearchFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/promotion/converters/populator/HktvPromotionsPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/promotion/impl/DefaultHktvPromotionFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/purchasedItems/impl/DefaultHktvPurchasedItemsFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/search/impl/DefaultHotSearchQueryFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/store/impl/DefaultStoreFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/store/impl/DefaultStoreRatingAndTypeFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/street/impl/DefaultStreetFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/user/impl/DefaultHktvUserFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/user/impl/ExtUserFacadeImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/variantproduct/populators/HktvCountVariantColorPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/voucher/impl/DefaultHktvVoucherFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/wishlist/impl/DefaultHktvMyListFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/wishlist/impl/DefaultWishlistFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facades/zone/impl/DefaultHktvZoneFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facads/order/impl/DefaultHktvMerchantDeliveryFeeRecordFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfacades/src/hk/com/hktv/facads/order/impl/HktvCartFacadeImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/category/provider/impl/HktvCategoryUtilServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/address/dao/impl/DefaultHktvAddressDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/address/dao/impl/DefaultHktvAddressWhitelistDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/address/service/impl/DefaultHktvAddressService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/address/service/impl/DefaultHktvAddressWhitelistService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/calculation/service/DefaultHktvCalculationService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/checkout/dao/impl/HktvInStorePickUpCheckoutDaoImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/checkout/service/impl/HktvInStorePickUpCheckoutServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/checkout/service/impl/HktvSingleSkuCheckoutServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/commerceservices/impl/DefaultHktvCommerceStockService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/consignment/dao/impl/HktvGoodsMeasureUnitDaoImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/consignment/service/impl/HktvGoodsMeasureUnitServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/credit/dao/impl/DefaultHktvPaidVoucherDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/credit/dao/impl/DefaultHktvVoucherDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/credit/service/impl/HktvCreditServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/credit/service/impl/HktvPaidVoucherServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/credit/service/impl/HktvProductReservedCodeServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/credit/service/impl/HktvVoucherServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/customer/dao/impl/DefaultHktvMemberShipLevelDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/customer/dao/impl/HktvPhoneContactInfoDaoImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/customer/impl/DefaultHktvMemberShipLevelService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/customer/impl/HktvCustomerServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/customer/impl/HktvPhoneContactInfoServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/delivery/deliveryRemarks/impl/DefaultHktvDeliveryRemarksService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/delivery/service/impl/DefaultDeliveryZoneService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/delivery/service/impl/hktvDeliveryService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/deliveryresource/service/impl/DefaultDeliveryResourceService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/ecoupon/dao/impl/DefaultHktvECouponDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/ecoupon/service/impl/DefaultHktvECouponService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/insurance/dao/impl/HktvInsuranceVoucherDaoImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/insurance/service/impl/HktvInsuranceVoucherServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/marketingoffer/service/impl/DefaultHktvMarketingOfferServiceImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/merchantDeliveryFee/dao/impl/DefaultHktvMerchantDeliveryFeeDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/merchantDeliveryFee/service/impl/DefaultHktvMerchantDeliveryFeeService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/nonBusinessDate/service/impl/DefaultHktvNonBusinessDateService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/order/dao/impl/DefaultHktvOrderEntryDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/order/service/impl/DefaultHktvOrderEntryService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/order/service/impl/DefaultHktvOrderService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/product/dao/impl/DefaultHktvDeliverableRegionDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/product/dao/impl/DefaultHktvFulfilmentBundleSetDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/product/dao/impl/DefaultHktvFulfilmentProductDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/product/dao/impl/DefaultHktvProductUserMaxDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/product/service/impl/DefaultHktvDeliverableRegionService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/product/service/impl/DefaultHktvFulfilmentBundleSetService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/product/service/impl/DefaultHktvFulfilmentProductService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/product/service/impl/DefaultHktvProductUserMaxService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/shop/service/impl/DefaultHktvShopService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/sms/dao/impl/DefaultHktvSmsDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/sms/service/impl/DefaultHktvSmsService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/store/dao/impl/DefaultStoreDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/store/service/impl/DefaultStoreService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/street/dao/impl/DefaultDeliveryUnitDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/street/service/impl/DefaultDeliveryUnitService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/timeslot/dao/impl/DefaultTimeSlotDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/timeslot/service/impl/DefaultTimeSlotService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/core/utils/HktvDateTimeUtils.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/delivery/impl/DefaultDeliveryFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/messagecenter/HktvMessageCenterAllMessageReadCommand.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/messagecenter/HktvMessageCenterMessageListCommand.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/messagecenter/HktvMessageCenterMessageReadCommand.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/messagecenter/HktvMessageCenterMultiMessageReadCommand.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/messagecenter/HktvMessageCenterUnreadCountCommand.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/messagecenter/impl/DefaultHktvMessageCenterFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/order/impl/DefaultFreeDeliveryOrderFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/facades/stock/impl/DefaultHktvStockFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/fulfilmentprocess/stock/service/impl/DefaultHktvStockService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/BilledAmountRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvAddressRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvCardBinRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvDeliveryTimeslotRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvFlatCodeRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvJointBankPromotionRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvNewCustomerRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvNewCustomerWithoutPaidOrderRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvPaidVoucher.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvPaymentRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvProductCategoryRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvPromotionVoucher.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvStoreRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvUserRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvVoucher.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvfulfilmentprocess/src/hk/com/hktv/voucher/jalo/HktvVoucherCodeOrderAmountRestriction.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/dao/impl/HktvRedisCartDeliveryRemarksDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/dao/impl/HktvRedisCommerceCartDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/dao/impl/HktvRedisOrderDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/dao/impl/HktvRedisOrderEntryDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/facade/impl/HktvRedisCheckoutFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/facade/impl/HktvRedisFreeDeliveryOrderFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/facade/impl/HktvRedisUnlimitedAddonFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/service/impl/HktvRedisCartService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/service/impl/HktvRedisCommerceCartService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/cart/strategy/HktvRedisCommerceCartCalculationStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/comms/service/impl/DefaultHktvRedisUcApiReviewStatService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/delivery/HktvRedisDeliveryResourceUsageDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/delivery/impl/DefaultHktvRedisPickPackResourceDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/facades/user/HktvRedisUserFacade.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/jalo/order/HktvRedisCart.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/merchantDeliveryFee/impl/HktvRedisMerchantDeliveryFeeService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/payment/impl/DefaultHktvRedisPaymentInfoService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/product/service/DefaultHktvRedisProductService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/recentlyViewedProduct/impl/DefaultHktvRecentlyViewedProductsRedisService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/salesnumber/dao/impl/DefaultHktvRedisSalesNumberDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/stock/impl/DefaultHktvRedisStockLevelDao.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvredis/src/hk/com/hktv/redis/stock/impl/DefaultHktvRedisStockService.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/AbstractHktvPageController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/pages/AccountPageController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/pages/AjaxPageController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/pages/CheckoutController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/pages/DeliveryAddressController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/pages/HomePageController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/pages/LoginPageController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/interceptors/beforeview/AnalyticsPropertiesBeforeViewHandler.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/src/hk/com/hktv/webservices/cart/impl/HktvNativeAppCartFacadeImpl.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/src/hk/com/hktv/webservices/cart/populator/HktvNativeAppCartPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/src/hk/com/hktv/webservices/cart/populator/HktvNativeAppCartProductPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/src/hk/com/hktv/webservices/cart/populator/HktvNativeAppExtendedCartPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/src/hk/com/hktv/webservices/cart/populator/HktvNativeAppOrderEntryPopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/src/hk/com/hktv/webservices/cart/populator/HktvNativeAppProductExtendedAttributePopulator.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/AccountController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/CartController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/CustomerECouponsController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/CustomersController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/HotKeywordsController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/MyListController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/NotifyMeController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/ProductsController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/PurchasedItemsController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/ServerToServerCustomerController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/ShareShoppingCartController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvwebservices/web/src/hk/com/hktv/webservices/v1/controller/WishListController.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/platform/ext/platformservices/src/de/hybris/platform/order/impl/DefaultCartFactory.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/platform/ext/platformservices/src/de/hybris/platform/order/strategies/calculation/impl/servicelayer/DefaultSLFindPriceStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/platform/ext/platformservices/src/de/hybris/platform/order/strategies/calculation/pdt/criteria/impl/DefaultPDTCriteriaFactory.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/platform/ext/platformservices/src/de/hybris/platform/order/strategies/calculation/pdt/impl/DefaultFindPriceValueInfoStrategy.java',
        'C:/work/hybris_docker/hybris_docker_hktvmall/bin/platform/ext/platformservices/src/de/hybris/platform/product/impl/DefaultProductService.java']
    methodPaths = get_method_paths(matching_files)
    for methodPath in methodPaths:
        check_method_exist(methodPath)
