
async def getPayment_method(arr_id_provider, ConditionsData):
    payment_method = ConditionsData['payment_method']
    payment = None
    for count_provider in payment_method:
        if count_provider.get('payment_distribution') == arr_id_provider:
            payment = str(count_provider.get('text'))
            break
    return payment

async def getDelivery_terms(deliveryParts, ConditionsData):
    delivery_terms = ConditionsData['delivery_terms']
    delivery = []
    
    for count_provider in delivery_terms:
        # if count_provider.get('delivery_timeframe') == arr_id_provider:
        data = count_provider.get('text')
        if isinstance(data, dict):
            for key in deliveryParts:
                value = data.get(key)
                if value and value.strip():
                    delivery.append(value)
    delivery = list(dict.fromkeys(delivery))
    return ", ".join(delivery)

async def getWarranty(warrantyParts, ConditionsData):
    warranty = ConditionsData['warranty']

    arr_warranty = []
    for count_provider in warranty:
        data = count_provider.get('text')
        if isinstance(data, dict):
            for key in warrantyParts:
                value = data.get(key)
                if value and value.strip():
                    arr_warranty.append(value)
    arr_warranty = list(dict.fromkeys(arr_warranty))
    return ", ".join(arr_warranty)

