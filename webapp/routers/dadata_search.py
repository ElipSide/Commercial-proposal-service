from dadata import Dadata

def dadata_inn(inn):
    token = "5c9a582c4549c1b027e0efed9b369721120e724c" #
    dadata = Dadata(token)
    result = dadata.suggest("party", inn)
    dadata.close()
    return result[0]['data']

def dadata_bic(bic):
    token = "5c9a582c4549c1b027e0efed9b369721120e724c" #
    dadata = Dadata(token)
    # result = dadata.suggest("party", inn)
    result = dadata.find_by_id("bank", bic)
    dadata.close()
    if result[0]['data']['bic'] == bic:
        return result[0]['data']
    else:
        return {}

