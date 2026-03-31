var dropArea 
var droppedContent
var UserData, lastmanagerInvoice, agreement_signed, invoice_sent, contract_ready

var mask, mask_client
// заполняет поля данными из бд
async function InsertData(){
  if(User_Info['access_level']=='manager'){  
    document.getElementById('companyManag').value = User_Info['company']
    document.getElementById('emailManag').value= User_Info['mail']
    document.getElementById('manag_SecondName').value= User_Info['middle_name']
    document.getElementById('manag_FirstName').value= User_Info['name']
    document.getElementById('telephoneManag').value= User_Info['phone_number']
    document.getElementById('telephone').innerText = document.getElementById('telephoneManag').value
    document.getElementById('telephone').href = `tel:${document.getElementById('telephoneManag').value}`
    document.getElementById('manag_SernameName').value= User_Info['surname']
    document.getElementById('manag_description').value= User_Info['description']
    document.getElementById('manag_post').value= User_Info['job_title']
        User_Info['description']!=''? document.getElementById('introduction').innerText = User_Info['description'] :0
    document.getElementById('manag_id_erp').value= User_Info['id_erp']
  }

  document.getElementById('Language_code').value= User_Info['language']

  document.getElementById('mask-inn-organization').value = check_info['inn']
  document.getElementById('AdresUser').value = check_info['address']
  document.getElementById('UserData_inputNumber').value = check_info['phone_number']
  document.getElementById('emailUser').value = check_info['email']
  document.getElementById('mask-bik').value = check_info['bic']
  document.getElementById('mask-account').value = check_info['checking_account']
  document.getElementById('SignerBlock').children[1].children[0].value = check_info['first_name']
  document.getElementById('SignerBlock').children[0].children[0].value = check_info['second_name'] 
  document.getElementById('SignerBlock').children[2].children[0].value = check_info['surname']
  document.getElementById('SignerBlock').children[3].children[0].value = check_info['position_user']
  document.getElementById('SelectProxy').value = check_info['acts_basis']
  document.getElementById('textareaValid').value = check_info['number_proxy']
  Comp_shortname.innerText = check_info['organization_shortname']
  UserValid()
  CheckCompany()
  Checkcheck()
  CheckSigner()
}


// Обновление полей в словарях для кп и в бд

function Update_KP(){

    var old_language = User_Info['language']

  if(User_Info['access_level']=='manager'){  
    User_Info= {
    'access_level': User_Info['access_level'],
    'company':  String(document.getElementById('companyManag').value) ,
    'data_reg': User_Info['data_reg'],
    'id_tg': ID_USER ,
    'language':document.getElementById('Language_code').value , // заменить на селектор
    'login': UserName,
    'mail': String(document.getElementById('emailManag').value),
    'middle_name': String(document.getElementById('manag_SecondName').value),
    'name': String(document.getElementById('manag_FirstName').value),
    'phone_number': String(document.getElementById('telephoneManag').value),
    'photo': User_Info['photo'],
    'surname': String(document.getElementById('manag_SernameName').value),
    "description": String(document.getElementById('manag_description').value),
    'id_erp': String(document.getElementById('manag_id_erp').value),
    'job_title': String(document.getElementById('manag_post').value),
    }
  }else{
    User_Info= {
      'access_level': User_Info['access_level'],
      'company': "",
      'data_reg': User_Info['data_reg'],
      'id_tg': ID_USER ,
      'language': document.getElementById('Language_code').value,
      'login': UserName,
      'mail': String(document.getElementById('emailUser').value),
      'middle_name': String(document.getElementById('SignerBlock').children[0].children[0].value),
      'name': String(document.getElementById('SignerBlock').children[1].children[0].value),
      'phone_number': String(document.getElementById('UserData_inputNumber').value),
      'photo': "",
      'surname': String(document.getElementById('SignerBlock').children[2].children[0].value),
      "description": '',
    }
  }
  
  check_info = {
    "id_tg": ID_USER,
    "analysis_link": "",
    "analytics_photo": "",
    "pdf_kp": check_info['pdf_kp'],
    "agreement_kp": false,
    "invoice_kp": "",
    "organization": "",
    "inn": String(document.getElementById('mask-inn-organization').value),
    "address": String(document.getElementById('AdresUser').value),
    "phone_number":String(document.getElementById('UserData_inputNumber').value),
    "email": String(document.getElementById('emailUser').value),
    "bic":String(document.getElementById('mask-bik').value),
    "checking_account": String(document.getElementById('mask-account').value),
    'first_name': String(document.getElementById('SignerBlock').children[1].children[0].value),
    'second_name': String(document.getElementById('SignerBlock').children[0].children[0].value),
    'surname': String(document.getElementById('SignerBlock').children[2].children[0].value),
    'position_user': String(document.getElementById('SignerBlock').children[3].children[0].value),
    "acts_basis": String(document.getElementById('SelectProxy').value),
    "number_proxy":String( document.getElementById('textareaValid').value),
    "contract_ready": check_info['contract_ready'],
    "agreement_signed":  check_info['agreement_signed'],
    "invoice_sent":  check_info['invoice_sent'],
    "lastmanager_invoice":  check_info['lastmanager_invoice'],
    "height": 0,
    "city":  check_info['city'],
    "organization_shortname": check_info['organization_shortname'],
    "organization_fullname": check_info['organization_fullname'],
    "ogrn": check_info['ogrn'],
    "kpp": check_info['kpp'],
    "bank_info": check_info['bank_info'],
    "corporate_account": check_info['corporate_account'],
  }
  formData = JSON.stringify({'check_info':check_info, 'User_Info': User_Info});
  $.ajax({
    type: 'post',
    url: '/off_bot/API/Update_check_info',
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
      console.log('обновили данные')
      if( old_language != User_Info['language']){
          hrefPage =window.location.href.includes('127.0.0.1')== true ? `http://127.0.0.1:8000/off_bot/offer/home`: `https://csort-news.ru/off_bot/offer/home`
          window.location.href =` ${hrefPage}?tg_id=${ID_USER}&username=${UserName}&deal=${Deal_id}`
      }

    },
    error: function (error) {
      Error_Message(`Update_check_info error ${ID_USER}\n${error}`)
    }
  })  

    
}



const AGREEMENT_GROUP_SOURCE_MAP = {
  'Sieve': function() { return All_Ids_ListSieve; },
  'sep_machine': function() { return All_ListMachine; },
  'elevator': function() { return All_elevator; },
  'compressor': function() { return All_compressor; },
  'photo_sorter': function() { return All_ListPhotoMachine; },
  'Pneumatic_feed': function() { return All_pneumatic_feed; },
  'extra_equipment': function() { return All_extra_equipment; },
  'laboratory_equipment': function() { return All_laboratory_equipment; },
  'Service': function() { return All_Service; },
  'attendance': function() { return All_attendance; }
}

function getPriceListForAgreement() {
  var price_listkp = []
  var Parent = document.getElementById('blockTable')
  for (var n = 3; n < Parent.children.length; n++) {
    price_listkp.push({
      'name': Number(Parent.children[n].children[1].id.split('__')[2]),
      'price': Number(Parent.children[n].children[4].children[0].innerText.replace(/\s/g, '')) / Number(Parent.children[n].children[3].children[0].value),
      'type': Parent.children[n].children[1].id.split('__')[1]
    })
  }
  return price_listkp
}

function getAgreementSourceByGroup(group_key) {
  return AGREEMENT_GROUP_SOURCE_MAP[group_key] ? AGREEMENT_GROUP_SOURCE_MAP[group_key]() : []
}

function findAgreementItem(group_key, id_el, provider) {
  var source = getAgreementSourceByGroup(group_key)
  if (!source || source.length === 0) {
    return undefined
  }

  var keyField = group_key === 'Sieve' ? 'id' : 'id_row'
  return source.find(function(item) {
    if (item[keyField] !== id_el) {
      return false
    }
    if (provider === undefined || provider === null) {
      return true
    }
    return item['id_provider'] == provider
  })
}

function getAgreementPriceEntry(price_listkp, id_el, group_key) {
  return price_listkp.find(function(item) {
    return item['name'] == id_el && item['type'] == group_key
  })
}

function buildSieveAgreementRow(El_item, count, priceEntry, group_value) {
  if (!El_item || !priceEntry) {
    return null
  }

  var sum = Number((priceEntry['price'] * count).toFixed(1))
  return {
    row: {
      'name': `решето ${El_item['Type'].toLowerCase()} ${(El_item['Count'].toFixed(1))}`,
      'count': count,
      'price': priceEntry['price'],
      'sum': sum,
      'id': `deleteRow__${group_value}__${El_item['id_row']}`,
      'id_erp': El_item['id_erp']
    },
    sum: sum
  }
}

function buildDefaultAgreementRow(group_key, group_value, El_item, count, priceEntry, ads) {
  if (!El_item || !priceEntry) {
    return null
  }

  var conf = group_key == 'photo_sorter' ? El_item['configuration'].replace('(Extra light)','') : ''
  var sum = Number((priceEntry['price'] * count).toFixed(1))
  var itemNamePrint = El_item['name_print'] || El_item['name']

  return {
    row: {
      'name': `${El_item['name']} ${conf}`,
      'name_print': itemNamePrint,
      'count': count,
      'price': priceEntry['price'],
      'sum': sum,
      'id': `deleteRow__${group_value}__${El_item['id_row']}`,
      'id_erp': El_item['id_erp'],
      'ads': ads || ''
    },
    sum: sum
  }
}

function collectProviderIdsFromKP() {
  var providers = new Set()

  for (const group_key in data_CP['group_info']) {
    const group = data_CP['group_info'][group_key]
    for (const id_el_str in group) {
      var id_el = Number(id_el_str)
      var item = findAgreementItem(group_key, id_el)
      if (item && item['id_provider'] !== undefined) {
        providers.add(item['id_provider'])
      }
    }
  }

  return Array.from(providers)
}

function buildAgreementRows(price_listkp, provider, options) {
  options = options || {}
  var includeAttendance = options.includeAttendance === true
  var list = []
  var sumTotal = 0

  for (const group_key in data_CP['group_info']) {
    const group = data_CP['group_info'][group_key]
    if (group_key === 'attendance' && !includeAttendance) {
      continue
    }

    for (const id_el_str in group) {
      var id_el = Number(id_el_str)
      var count = group[id_el_str]
      var ads = group_key === 'attendance' ? 'ads' : ''
      var El_item = findAgreementItem(group_key, id_el, provider)
      var priceEntry = getAgreementPriceEntry(price_listkp, id_el, group_key)
      var builtRow = group_key === 'Sieve'
        ? buildSieveAgreementRow(El_item, count, priceEntry, group)
        : buildDefaultAgreementRow(group_key, group, El_item, count, priceEntry, ads)

      if (!builtRow) {
        continue
      }

      list.push(builtRow.row)
      sumTotal += builtRow.sum
    }
  }

  return {
    list: list,
    sum: sumTotal
  }
}

// Сбор данных и создание договора
function GetAgreement(){  
  if(data_CP['group_info']['attendance'][3] != undefined && address_user.value ==''){
    BadToast(I18N.t('enterDeliveryAddress'))
    address_user.style.borderColor = 'red'
    Scroll_startBlock(document.getElementById('address_user'))
    return
  }else{
    data_CP['additional_info']['address_delivery']= address_user.value
    UpdateCPlist(data_CP, List_CP, 'offer')
  }

  tg.MainButton.hide();
  Telegram.WebApp.offEvent('mainButtonClicked', GetAgreement)

  CheckCompany()
  Checkcheck()
  CheckSigner()

  var price_listkp =[]
  var Parent = document.getElementById('blockTable')
  for (var n = 3; n < Parent.children.length; n++) {
    price_listkp.push({
      'name':Number(Parent.children[n].children[1].id.split('__')[2]),
      'price': Number(Parent.children[n].children[4].children[0].innerText.replace(/\s/g, ''))/Number(Parent.children[n].children[3].children[0].value),
      'type':Parent.children[n].children[1].id.split('__')[1]
    })
  }
  let Oneprovider_list = new Set();
  for (const group_key in data_CP['group_info']) {
    const group = data_CP['group_info'][group_key];
    for (const id_el_str in group) {
      var  id_el = Number(id_el_str);
      switch (group_key) {
        case 'Sieve':
          const El_Sieve = All_Ids_ListSieve.find(f => f['id'] === id_el);
          if (El_Sieve) Oneprovider_list.add(El_Sieve['id_provider']);
          break;
        case 'sep_machine':
          const El_machine = All_ListMachine.find(f => f['id_row'] === id_el);
          if (El_machine) Oneprovider_list.add(El_machine['id_provider']);
          break;
        case 'elevator':
          const El_elevator = All_elevator.find(f => f['id_row'] === id_el);
          if (El_elevator) Oneprovider_list.add(El_elevator['id_provider']);
          break;
        case 'compressor':
          const El_comp = All_compressor.find(f => f['id_row'] === id_el);
          if (El_comp) Oneprovider_list.add(El_comp['id_provider']);

          break;
        case 'photo_sorter':
          const El_photo_machine = All_ListPhotoMachine.find(f => f['id_row'] === id_el);
          if (El_photo_machine) Oneprovider_list.add(El_photo_machine['id_provider']);
          break;
        case 'Pneumatic_feed':
          const El_Pneumatic_feed = All_pneumatic_feed.find(f => f['id_row'] === id_el);
          if (El_Pneumatic_feed) Oneprovider_list.add(El_Pneumatic_feed['id_provider']);
          break;

        case 'extra_equipment':
          const El_extra_equipment = All_extra_equipment.find(f => f['id_row'] === id_el);
          if (El_extra_equipment) Oneprovider_list.add(El_extra_equipment['id_provider']);
          break;
        case 'laboratory_equipment':
          const El_laboratory_equipment = All_laboratory_equipment.find(f => f['id_row'] === id_el);
          if (El_laboratory_equipment) Oneprovider_list.add(El_laboratory_equipment['id_provider']);
          break;

          
        case 'Service':
          const El_Serv = All_Service.find(f => f['id_row'] === id_el);
          if (El_Serv) Oneprovider_list.add(El_Serv['id_provider']);
          break;
      }
    }
  }
  Oneprovider_list = Array.from(Oneprovider_list);
  var DataList = []
  check_info['agreement_kp'] = true
  if(User_Info['access_level']=='manager'){  

    if(ID_provider == 3){ // договора для сисорта
      data = Manager_Csort(Oneprovider_list, price_listkp)
      DataList= data
    }
    else{// договора для остальных
      data = Manager_Other(Oneprovider_list, price_listkp)
      DataList= data
    }
  }
  
  // договор клиента и менеджера
  var ListCheck_Agreement = []
  var Sum_ListCheck = 0
  for (const group_key in data_CP['group_info']) {
    const group = data_CP['group_info'][group_key];
    for (const id_el_str in group) {
      const id_el = Number(id_el_str);
      let count  = group[id_el_str]
      let El_item = []
      let ads = ''
      
      switch (group_key) {
        case 'Sieve':
          El_item = All_Ids_ListSieve.find(f => f['id'] === id_el );
          if(El_item== [] || El_item== undefined){continue}
          sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))

          ListCheck_Agreement.push({
            'name': `решето ${El_item['Type'].toLowerCase()} ${(El_item['Count'].toFixed(1))}` ,
            'count' : count,
            'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
            'sum': sum,
            'id': `deleteRow__${group}__${El_item['id_row']}`,
            "id_erp": El_item['id_erp'],
          })
          Sum_ListCheck+= sum
          El_item = undefined
          break;
        case 'sep_machine':
          El_item = All_ListMachine.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
        case 'elevator':
          El_item = All_elevator.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
        case 'compressor':
          El_item = All_compressor.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
        case 'photo_sorter':
          El_item = All_ListPhotoMachine.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
        case 'Pneumatic_feed':
          El_item = All_pneumatic_feed.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
          
        case 'extra_equipment':
          El_item = All_extra_equipment.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
        case 'laboratory_equipment':
          El_item = All_laboratory_equipment.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;

          
        case 'Service':
          El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
        case 'attendance':
          El_item = All_attendance.filter(function(f) { return  f['id_row'] === id_el})[0]
          ads = "ads"
          break;
        }
      if(El_item!= undefined){
        if(group_key == 'photo_sorter'){
          conf =El_item['configuration'].replace('(Extra light)','') }
        else{conf = ''}
        sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))
        console.log(El_item)
        const itemNamePrint = El_item['name_print'] || El_item['name'];
        // const displayName = El_item['name_print'] != undefined ?
        //   `${El_item['name_print']} ${conf}` :
        //   `${El_item['name']} ${conf}`;

        ListCheck_Agreement.push({
            'name': `${El_item['name']} ${conf}`,
            'name_print': itemNamePrint,
            'count' : count,
            'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
            'sum': sum,
            'id': `deleteRow__${group}__${El_item['id_row']}`,
            "id_erp": El_item['id_erp'],
            'ads': ads
        })
        Sum_ListCheck+=sum
      }
    }
  }

  check_info['agreement_kp'] = true
  data = ReturnData(ID_provider, ListCheck_Agreement)
  data['Preambula'] = document.getElementById('preambulBlock').value
  data['NameFile'] = data['seller']['organization_shortname'].replace(/"/g, '');
  data['id_provider'] = ID_provider
  data['key'] = key
  data['sum'] =  Sum_ListCheck
  data['sale'] =  data_CP['sale']

  data['Chat_id'] =  ID_USER
  data['date'] =  List_CP['creation_date']
  data['additional_info'] = data_CP['additional_info']
  data['UserName'] = UserName
  data['page'] ='offer'
  if(User_Info['access_level']=='manager'){  
    data['Id_manager'] =  ID_USER
    data['client'] = false
  }
  else{
    data['Id_manager'] =  ''
    data['client'] = true
  }
  DataList.push(data)
  if(User_Info['access_level']=='client'){  
    if(ID_provider == 3){ // договора для сисорта
      data = Manager_Csort(Oneprovider_list, price_listkp)
      DataList.push(...data);
    }
  }
  else{
    DataList = DataList.reverse();

  }
  GoodToast(I18N.t('contractWillBeSent'))
  BackUserInfo()
  // UserInfo_Block.style.display = 'flex'
  // ListFullData.style.display = 'none'
  formData = JSON.stringify( DataList);
  console.log(DataList)
  $.ajax({
    type: 'post',
    url: '/off_bot/API/Sieve_GetAgreement',
    data: formData,
    processData: false,
    contentType: false,
    async: true,
    success: function(data){
      Check_counterparty()
    },
    error: function (error) {
      Error_Message(`Sieve_GetAgreement ${ID_USER}\n${error}`)
    } 
  }) 
  
}

// Сбор данных и для создания договора менеджерами сисорта
function Manager_Csort(Oneprovider_list, price_listkp){
  var DataList = []
  for (var n = 0; n <= Oneprovider_list.length-1; n++){
    var provider = Oneprovider_list[n]
    if(provider==ID_provider){continue}

    var agreementData = buildAgreementRows(price_listkp, provider)
    var ListCheck_Agreement = agreementData.list
    var Sum_ListCheck = agreementData.sum

    data = ReturnDataCompany(ID_provider, provider, ListCheck_Agreement)
    Preambula_Buy = List_Provider.filter(function(f) { return f['id'] == 3})[0]['preamble_buy']
    Preambula_Sell = List_Provider.filter(function(f) { return f['id'] == provider})[0]['preamble_sell']
    data['Preambula'] = `${Preambula_Buy} и ${Preambula_Sell}`
    data['buyer']['user_id'] = ID_USER
    data['NameFile'] = data['seller']['organization_shortname'].replace(/"/g, '');
    data['id_provider'] = ID_provider
    data['key'] = key
    data['sum'] = Sum_ListCheck
    data['Chat_id'] = List_Provider.filter(function(f) { return f['id'] == provider})[0]['chat_id']
    DataList.push(data)
  }

  return DataList
}

function Csort_agrement(Oneprovider_list, price_listkp){
  var DataList = []
  for (var n = 0; n <= Oneprovider_list.length-1;n++){
    var ListCheck_Agreement = []
    var Sum_ListCheck = 0
    provider = Oneprovider_list[n]
    if(provider==ID_provider || provider==3){continue}

    for (const group_key in data_CP['group_info']) {
      const group = data_CP['group_info'][group_key];
      for (const id_el_str in group) {
        const id_el = Number(id_el_str);
        let count  = group[id_el_str]
        let El_item = []
        switch (group_key) {
          case 'Sieve':
            El_item = All_Ids_ListSieve.find(f => f['id'] === id_el && f['id_provider'] == provider);
            if(El_item== [] || El_item== undefined){continue}
            sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))

            ListCheck_Agreement.push({
              'name': `решето ${El_item['Type'].toLowerCase()} ${(El_item['Count'].toFixed(1))}` ,
              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': sum,
              'id': `deleteRow__${group}__${El_item['id_row']}`,
              "id_erp": El_item['id_erp']
            })
            Sum_ListCheck+= sum
            El_item = undefined
            break;
          case 'sep_machine':
            El_item = All_ListMachine.filter(function(f) { return  f['id_row'] === id_el  && f['id_provider'] == provider})[0]
            break;
          case 'elevator':
            El_item = All_elevator.filter(function(f) { return  f['id_row'] === id_el  && f['id_provider'] == provider})[0]
            break
          case 'compressor':
            El_item = All_compressor.filter(function(f) { return  f['id_row'] === id_el  && f['id_provider'] == provider})[0]
            break;
          case 'photo_sorter':
            El_item = All_ListPhotoMachine.filter(function(f) { return  f['id_row'] === id_el && f['id_provider'] == provider})[0]
            break;
          case 'Pneumatic_feed':
            El_item = All_pneumatic_feed.filter(function(f) { return  f['id_row'] === id_el && f['id_provider'] == provider})[0]
            break;

            
          case 'extra_equipment':
            El_item = All_extra_equipment.filter(function(f) { return  f['id_row'] === id_el && f['id_provider'] == provider})[0]
            break;
          case 'laboratory_equipment':
            El_item = All_laboratory_equipment.filter(function(f) { return  f['id_row'] === id_el && f['id_provider'] == provider})[0]
            break;

            
          case 'Service':
            El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el && f['id_provider'] == provider})[0]
            break;
 

        }
        if(El_item!= undefined){
          if(group_key == 'photo_sorter'){ conf =El_item['configuration'].replace('(Extra light)','') }else{conf = ''}
          sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))

          // console.log(El_item['name'])
          ListCheck_Agreement.push({
              'name': `${El_item['name']} ${conf}`,

              'name_print': El_item['name'],
              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': sum,
              'id': `deleteRow__${group}__${El_item['id_row']}`,
              "id_erp": El_item['id_erp']
          })
          Sum_ListCheck+=sum
        }
      }
    }
    data = ReturnDataCompany(3, provider, ListCheck_Agreement)
    Preambula_Buy = List_Provider.filter(function(f) { return f['id'] == 3})[0]['preamble_buy']
  
    Preambula_Sell = List_Provider.filter(function(f) { return f['id'] == provider})[0]['preamble_sell']
    data['Preambula'] = `${Preambula_Buy} и ${Preambula_Sell}`
    data['buyer']['user_id'] = ID_USER
    data['NameFile'] = data['seller']['organization_shortname'].replace(/"/g, '');
    data['id_provider'] = 3
    data['key'] = key
    data['sum'] =  Sum_ListCheck
    data['Chat_id'] =  List_Provider.filter(function(f) { return f['id'] == provider})[0]['chat_id']
    DataList.push(data)
  }
  return DataList

}
// функция для возврата елементов группы в опрделенном формате
function returnList(){
  var ListCheck_Agreement = []
  var Sum_ListCheck = 0
  for (const group_key in data_CP['group_info']) {
    const group = data_CP['group_info'][group_key];
    for (const id_el_str in group) {
      const id_el = Number(id_el_str);
      let count  = group[id_el_str]
      let El_item = []
      switch (group_key) {
        case 'Sieve':
          El_item = All_Ids_ListSieve.find(f => f['id'] === id_el);
          if(El_item== [] || El_item== undefined){continue}
          sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))

          ListCheck_Agreement.push({
            'name': `решето ${El_item['Type'].toLowerCase()} ${(El_item['Count'].toFixed(1))}` ,
            'count' : count,
            'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
            'sum': sum,
            'id': `deleteRow__${group}__${El_item['id_row']}`,
            "id_erp": El_item['id_erp']
          })
          Sum_ListCheck+= sum
          El_item = undefined
          break;
        case 'sep_machine':
          El_item = All_ListMachine.filter(function(f) { return  f['id_row'] === id_el })[0]
          break;

        case 'elevator':
          El_item = All_elevator.filter(function(f) { return  f['id_row'] === id_el })[0]
          break;
          
        case 'compressor':
          El_item = All_compressor.filter(function(f) { return  f['id_row'] === id_el })[0]
          break;
        case 'photo_sorter':
          El_item = All_ListPhotoMachine.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;

        case 'Pneumatic_feed':
        El_item = All_pneumatic_feed.filter(function(f) { return  f['id_row'] === id_el})[0]
        break;

          
        case 'extra_equipment':
          El_item = All_extra_equipment.filter(function(f) { return  f['id_row'] === id_el })[0]
          break;
        case 'laboratory_equipment':
          El_item = All_laboratory_equipment.filter(function(f) { return  f['id_row'] === id_el })[0]
          break;
          
        case 'Service':
          El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
      }
      if(El_item!= undefined){
        sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))

        // console.log(El_item['name'])
        ListCheck_Agreement.push({
            'name': El_item['name'],
            'count' : count,
            'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
            'sum': sum,
            'id': `deleteRow__${group}__${El_item['id_row']}`,
            "id_erp": El_item['id_erp']
        })
        Sum_ListCheck+=sum
      }
    }
  }

  return ListCheck_Agreement, Sum_ListCheck
}


// Сбор данных и создание счета
function Getcheck(){
  CheckCompany()
  Checkcheck()
  CheckSigner()
  if(Name_CheckBlock.style.backgroundColor =='white' || Name_CompanyBlock.style.backgroundColor  =='white'){
    BadToast(I18N.t('fillCompanyAndInvoice'))
    return
  }
  var price_listkp =[]
  var Parent = document.getElementById('blockTable')
  for (var n = 3; n < Parent.children.length; n++) {
    price_listkp.push({
      'name':Number(Parent.children[n].children[1].id.split('__')[2]),
      'price': Number(Parent.children[n].children[4].children[0].innerText.replace(/\s/g, ''))/Number(Parent.children[n].children[3].children[0].value),
      'type':Parent.children[n].children[1].id.split('__')[1]
    })
  }
  let Oneprovider_list = new Set();
  for (const group_key in data_CP['group_info']) {
    const group = data_CP['group_info'][group_key];
    for (const id_el_str in group) {
      var  id_el = Number(id_el_str);
      switch (group_key) {
        case 'Sieve':
          const El_Sieve = All_Ids_ListSieve.find(f => f['id'] === id_el);
          if (El_Sieve) Oneprovider_list.add(El_Sieve['id_provider']);
          break;
        case 'sep_machine':
          const El_machine = All_ListMachine.find(f => f['id_row'] === id_el);
          if (El_machine) Oneprovider_list.add(El_machine['id_provider']);
          break;
        case 'elevator':
          const El_elevator = All_elevator.find(f => f['id_row'] === id_el);
          if (El_elevator) Oneprovider_list.add(El_elevator['id_provider']);
          break;
        case 'compressor':
          const El_comp = All_compressor.find(f => f['id_row'] === id_el);
          if (El_comp) Oneprovider_list.add(El_comp['id_provider']);

          break;
        case 'photo_sorter':
          const El_photo_machine = All_ListPhotoMachine.find(f => f['id_row'] === id_el);
          if (El_photo_machine) Oneprovider_list.add(El_photo_machine['id_provider']);
          break;
        case 'Pneumatic_feed':
          const El_Pneumatic_feed = All_pneumatic_feed.find(f => f['id_row'] === id_el);
          if (El_Pneumatic_feed) Oneprovider_list.add(El_Pneumatic_feed['id_provider']);
          break;

          
        case 'extra_equipment':
          const El_extra_equipment = All_extra_equipment.find(f => f['id_row'] === id_el);
          if (El_extra_equipment) Oneprovider_list.add(El_extra_equipment['id_provider']);
          break;

        case 'laboratory_equipment':
          const El_laboratory_equipment = All_laboratory_equipment.find(f => f['id_row'] === id_el);
          if (El_laboratory_equipment) Oneprovider_list.add(El_laboratory_equipment['id_provider']);
          break;
          
        case 'Service':
          const El_Serv = All_Service.find(f => f['id_row'] === id_el);
          if (El_Serv) Oneprovider_list.add(El_Serv['id_provider']);
          break;
      }
    }
  }
  Oneprovider_list = Array.from(Oneprovider_list);
  var DataList = []
  check_info['agreement_kp'] = true
  if(User_Info['access_level']=='manager'){  

    if(ID_provider == 3){ // договора для сисорта
      data = Manager_Csort(Oneprovider_list, price_listkp)
      DataList= data
    }
    else{// договора для остальных
      data = Manager_Other(Oneprovider_list, price_listkp)
      DataList= data
    }
  }

  // договор клиента и менеджера
    var ListCheck_Agreement = []
    var Sum_ListCheck = 0
    for (const group_key in data_CP['group_info']) {
      const group = data_CP['group_info'][group_key];
      for (const id_el_str in group) {
        const id_el = Number(id_el_str);
        let count  = group[id_el_str]
        let El_item = []
        var ads = ''
        switch (group_key) {
          case 'Sieve':
            El_item = All_Ids_ListSieve.find(f => f['id'] === id_el );
            if(El_item== [] || El_item== undefined){continue}
            sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))

            ListCheck_Agreement.push({
              'name': `решето ${El_item['Type'].toLowerCase()} ${(El_item['Count'].toFixed(1))}` ,
              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': sum,
              'id': `deleteRow__${group}__${El_item['id_row']}`,
              "id_erp": El_item['id_erp']
            })
            Sum_ListCheck+= sum
            El_item = undefined
            break;
          case 'sep_machine':
            El_item = All_ListMachine.filter(function(f) { return  f['id_row'] === id_el  })[0]
            break;
            
          case 'elevator':
            El_item = All_elevator.filter(function(f) { return  f['id_row'] === id_el  })[0]
            break;
          case 'compressor':
            El_item = All_compressor.filter(function(f) { return  f['id_row'] === id_el  })[0]
            break;
          case 'photo_sorter':
            El_item = All_ListPhotoMachine.filter(function(f) { return  f['id_row'] === id_el  })[0]
            break;
          case 'Pneumatic_feed':
            El_item = All_pneumatic_feed.filter(function(f) { return  f['id_row'] === id_el  })[0]
            break;

            
          case 'extra_equipment':
            El_item = All_extra_equipment.filter(function(f) { return  f['id_row'] === id_el})[0]
            break;
          case 'laboratory_equipment':
            El_item = All_laboratory_equipment.filter(function(f) { return  f['id_row'] === id_el})[0]
            break;
            
          case 'Service':
            El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el})[0]
            break;
          case 'attendance':
            El_item = All_attendance.filter(function(f) { return  f['id_row'] === id_el})[0]
            ads = "ads"
            break;
        }
        if(El_item!= undefined){
          if(group_key == 'photo_sorter'){ conf =El_item['configuration'].replace('(Extra light)','') }else{conf = ''}
          console.log(id_el, group_key)
          console.log(price_listkp)
          sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))
          console.log(sum)
          const itemNamePrint = El_item['name_print'] || El_item['name'];

          // console.log(El_item['name'])
          ListCheck_Agreement.push({
              'name': `${El_item['name']} ${conf}`,
              'name_print': itemNamePrint,

              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': sum,
              'id': `deleteRow__${group}__${El_item['id_row']}`,
              "id_erp": El_item['id_erp'],
              'ads': ads

          })
          Sum_ListCheck+=sum
        }
      }
    }
    

    check_info['invoice_sent'] = true
  data = ReturnData(ID_provider, ListCheck_Agreement)
  data['id_provider'] = ID_provider
  data['NameFile'] = data['seller']['organization_shortname'].replace(/"/g, '');
  data['key'] = key
  data['sum'] =  Sum_ListCheck
  data['sale'] =  data_CP['sale']

  data['Chat_id'] =  ID_USER
  data['date'] =  List_CP['creation_date']
  data['additional_info'] = data_CP['additional_info']
  data['UserName'] = UserName
  data['page'] ='offer'


  if(User_Info['access_level']=='manager'){  
    data['Id_manager'] =  ID_USER
    data['client'] = false
  }
  else{
    data['Id_manager'] =  ''
    data['client'] = true
  }

  DataList.push(data)
  DataList = DataList.reverse();
  GoodToast(I18N.t('invoiceWillBeSent'))
  formData = JSON.stringify( DataList);
  $.ajax({
    type: 'post',
    url: '/off_bot/API/Sieve_GetCheck',
    data: formData,
    processData: false,
    contentType: false,
    async: true,
    success: function(data){
      // data_CP["id_send_check"] = data

      // GetMessageKP('Обновленное КП',`Контрагент ${check_info['organization_shortname']}\nТелефон: <a href="tel:+${check_info['phone_number']}">+${check_info['phone_number']}</a>`)
      Check_counterparty()
    },
    error: function (error) {
      Error_Message(`Sieve_GetCheck ${ID_USER}\n${error}`)
    } 
  }) 


}


var key_check
// созданиме словаря с данными для создания договора/счета
function ReturnData(id_prov, infoList){
  Update_KP()
  ListCheck = ReturnListCheck(infoList)
  if(User_Info['access_level']=='manager'){  

    data={
      'List':ListCheck,
      'CreateIn1сErp': false,
      'CategoryId':1,
      'number':'1',
      'nds':'включает',
      'id_erp_manager':User_Info['id_erp'],
      'FIO_manager':`${User_Info['name']} ${User_Info['middle_name']}`,
      'terms_payment': terms_payment,
      'Delivery_time' :Delivery_time,
      'Guarantee' :Guarantee,
      'Delivery_text': document.getElementById('deliveryBlock').value,
      'Guarantee_text': document.getElementById('WarrantyBlock').value,
      'terms_payment_text': document.getElementById('paymentyBlock').value,
      'city': check_info['city'],
      'buyer':{
          'user_id': ID_USER,
          'city': String(check_info['city']),
          'Date_create': check_info['Create_KP'],
          'organization_fullname': check_info['organization_fullname'],
          'organization_shortname': check_info['organization_shortname'],
          'inn': String(check_info['inn']),
          'ogrn':String(check_info['ogrn']),
          'kpp':String(check_info['kpp']),
          'address': check_info['address'],
          'phone_number': String(check_info['phone_number']),
          'email': check_info['email'],
          'bic':String(check_info['bic']),
          'bank_info': String(check_info['bank_info']),
          'checking_account': String(check_info['checking_account']),
          'corporate_account': String(check_info['corporate_account']),
          'first_name': String(check_info['first_name']),
          'second_name':check_info['second_name'],
          'surname': check_info['surname'],
          'position_user':check_info['position_user'],
          'acts_basis': check_info['acts_basis'],
          'number_proxy':check_info['number_proxy'],
      },
      'seller':List_Provider.filter(function(f) { return f['id'] == id_prov})[0]
    }
  }else{
    data={
      'List':ListCheck,
      'number':'1',
      'id_erp_manager':'',
      'FIO_manager':'',
      'nds':'включает',
      'terms_payment': terms_payment,
      'Delivery_time' :Delivery_time, 
      'Guarantee' :Guarantee,
      'Delivery_text': document.getElementById('deliveryBlock').value,
      'Guarantee_text': document.getElementById('WarrantyBlock').value,
      'terms_payment_text': document.getElementById('paymentyBlock').value,
      'city': check_info['city'],
      'buyer':{
          'user_id': ID_USER,
          'city': String(check_info['city']),
          'Date_create': check_info['Create_KP'],
          'organization_fullname': check_info['organization_fullname'],
          'organization_shortname': check_info['organization_shortname'],
          'inn': String(check_info['inn']),
          'ogrn':String(check_info['ogrn']),
          'kpp':String(check_info['kpp']),
          'address': check_info['address'],
          'phone_number': String(check_info['phone_number']),
          'email': check_info['email'],
          'bic':String(check_info['bic']),
          'bank_info': String(check_info['bank_info']),
          'checking_account': String(check_info['checking_account']),
          'corporate_account': String(check_info['corporate_account']),
          'first_name': String(check_info['first_name']),
          'second_name':check_info['second_name'],
          'surname': check_info['surname'],
          'position_user':check_info['position_user'],
          'acts_basis': check_info['acts_basis'],
          'number_proxy':check_info['number_proxy'],
      },
      'seller':List_Provider.filter(function(f) { return f['id'] == ID_provider})[0]
    }
  }
  return data
}

// созданиме словаря с данными компании для создания договора/счета
function ReturnDataCompany(id_prov,id_seller, infoList){
  Update_KP()
  ListCheck = ReturnListCheck(infoList)
  if(User_Info['access_level']=='manager'){  
    id_erp_manager = User_Info['id_erp']
    FIO_manager = `${User_Info['name']} ${User_Info['middle_name']}`
  }
  else{
    id_erp_manager = ''
    FIO_manager = ''
  }

  data={
    'List':ListCheck,
    'number':'1',
    'nds':'включает',
    'id_erp_manager':id_erp_manager,
    'FIO_manager':FIO_manager,
    'terms_payment': terms_payment,
    'Delivery_time' :Delivery_time, 
    'Guarantee' :Guarantee,
    'Delivery_text': document.getElementById('deliveryBlock').value,
    'Guarantee_text': document.getElementById('WarrantyBlock').value,
    'terms_payment_text': document.getElementById('paymentyBlock').value,
    'city': check_info['city'],
    'buyer':List_Provider.filter(function(f) { return f['id'] == id_prov})[0],
    'seller':List_Provider.filter(function(f) { return f['id'] == id_seller})[0]
  }

  return data
}
// разметка словаря под необходимый формат
function ReturnListCheck(infoList){
  ListCheck = infoList.map(item => ({
    number: infoList.indexOf(item)+1,
    name: item.name,
    name_print: item.name_print,
    count: item.count,
    count_name: 'шт',
    price: item.price,
    sum:item.sum,
    id_erp:item.id_erp,
    ads: item.ads
  }));
  return ListCheck
}


// поиск информации о компании по инн через dadata, заполненние найденных полей и обновление кп
function SearchInn(){
  $.ajax({
    type: 'get',
    url:`/off_bot/API/SearchInn_dadata/${String(document.getElementById('mask-inn-organization').value)}`,
    processData: false,
    contentType: false,
    success: function(data){
      document.getElementById('AdresUser').value = data['address']['unrestricted_value']!= null? data['address']['unrestricted_value']: ''
      document.getElementById('UserData_inputNumber').value = data['phones']!= null &&  document.getElementById('UserData_inputNumber').value == '' ? data['phones']: document.getElementById('UserData_inputNumber').value
      document.getElementById('emailUser').value = data['emails']!= null && document.getElementById('emailUser').value == ''? data['emails']: document.getElementById('emailUser').value
      
      check_info['city']  = data['address']['data']['city'] != null ? data['address']['data']['city'] : data['address']['data']['settlement']
      check_info['ogrn'] = data['ogrn']
      data['kpp'] != undefined ? check_info['kpp']= data['kpp']: 0
      check_info['organization_fullname'] = data['name']['full_with_opf']
      check_info['organization_shortname'] = data['name']['short_with_opf']
      Comp_shortname.innerText = data['name']['short_with_opf']
      if(data['management']!= undefined){
        document.getElementById('SignerBlock').children[0].children[0].value = data['management']['name'].split(' ')[0]
        document.getElementById('SignerBlock').children[1].children[0].value = data['management']['name'].split(' ')[1]
        data['management']['name'].split(' ')[2] != undefined ? document.getElementById('SignerBlock').children[2].children[0].value = data['management']['name'].split(' ')[2]: 0
        document.getElementById('SignerBlock').children[3].children[0].value = data['management']['post']
      }
      else{
        document.getElementById('SignerBlock').children[0].children[0].value = data['fio']['surname'] 
        document.getElementById('SignerBlock').children[1].children[0].value = data['fio']['name'] 
        data['fio']['patronymic'] != undefined ? document.getElementById('SignerBlock').children[2].children[0].value = data['fio']['patronymic']: 0
        document.getElementById('SignerBlock').children[3].children[0].value = data['opf']['full']
      }
      
      Update_KP()

      },
      error: function (error) {
        Error_Message(`SearchInn_dadata ${ID_USER}\n${error}`)
      } 
  }) 
}
// поиск информации о компании по бик через dadata, заполненние найденных полей и обновление кп
function SearchBic(){
  $.ajax({
    type: 'get',
    url:`/off_bot/API/SearchBic_dadata/${String(document.getElementById('mask-bik').value)}`,
    processData: false,
    contentType: false,
    success: function(data){
      check_info['bank_info'] =  `${data['name']['payment']} ${data['payment_city']}`
      check_info['corporate_account'] = data['correspondent_account']
      data['kpp'] != undefined ? check_info['kpp']= data['kpp']: 0
      Update_KP()
      },
      error: function (error) {
        Error_Message(`SearchBic_dadata ${ID_USER}\n${error}`)
      } 
  }) 
}
// переход к сдлеке в битрикс24
function Open_deal_bitrix() {
    if (
        typeof data_CP !== 'undefined' &&
        data_CP.additional_info &&
        data_CP.additional_info.link_deal
    ) {
        const url = data_CP.additional_info.link_deal;

        // открытие в новой вкладке
        window.open(url, '_blank', 'noopener,noreferrer');
    } else {
        console.error('Ссылка на сделку Bitrix не найдена');
    }
}

//  Создание пдф и отправка пользователю
function SavePDF(togl){
  Deal_id !=0? togl='Bitrix': 0

  if(togl!='Bitrix'){  GoodToast(I18N.t('kpWillBeSent'))}
  
  else{ 
    WarningToast(I18N.t('creatingDeal'))
    mainBlock.style.filter = 'blur(2px)'
    mainBlock.style.pointerEvents = 'none'
    // WarningToast(I18N.t('creatingDeal_time'))
  }

  document.getElementById('GetKP_button').style.display = 'none'
  if(User_Info['access_level']=='manager'){  
    FIO_manager = `${User_Info['name']} ${User_Info['middle_name']}`
    client= 'manager'
  }
  else{
    FIO_manager = ''
    client='client'
  }
  DataList={
    'sum': data_CP['price'],
    'date': List_CP['creation_date'],
    'FIO': FIO_manager,
    'client': client
  }
  formData = JSON.stringify( DataList);


  $.ajax({
    url:`/off_bot/API/Sieve_SavePDF/${ID_USER}/${key}`,
    data: formData,
    type: 'post',
    success: function (data) {
      if(togl=='Bitrix'){
        Getdeal_Bitrix()
      }
      if(data==false){
        BadToast(I18N.t('kpUnavailable'))
      }
      },
      error: function (error) {
        Error_Message(`Sieve_SavePDF ${ID_USER}\n${error}`)
      } 
  });

}


// обработчик фотографии 
function Manager_images_load(id){
  var ID_M = id.split('_')[1]

  document.getElementById("fileElem").value = ''
  var el = document.getElementById("fileElem");
  if (el) {
    el.click();
  }
}
// сохранение фотографии на сервер
function handleFiles(files_photo, id) {
  var files_photo = document.getElementById(`fileElem`).files
  TypeForm = new FormData();
  TypeForm.append(`file`, files_photo[0], ID_USER)
  document.getElementById('BlockmanagerPhoto').src = ''
  ToglCheckAnalys = true
  formData = TypeForm;
  $.ajax({
    type: 'POST',
    url: `/off_bot/API/Manager_SavePhoto/${ID_USER}`,
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
      GoodToast(I18N.t('photoUploaded'))
      currentTime = Math.floor(new Date().getTime() / 1000);
      document.getElementById('BlockmanagerPhoto').src =`${data}?u=currentTime`
      User_Info['photo'] = data
      Update_KP()
    },
    error: function (error) {
      Error_Message(`Manager_SavePhoto ${ID_USER}\n${error}`)
    } 
  })  
  
}


// Запрос и работа с данными для транспортного калькулятора 
function addNewCheck(){
  var id_deal = document.getElementById('Select_elevator').children[1].value
  id_deal = id_deal.replace(',','.')
  $.ajax({
    type: 'get',
    url: `/off_bot/API/GetCalkElevator/${id_deal}`,
    processData: false,
    contentType: false,
    success: function(data){
      console.log(data)

      var el_height = 
      parseFloat(data['modelSize']['height'] || 0) +
      parseFloat(data['modelSize']['top_length'] || 0) +
      parseFloat(data['modelSize']['bottom_length'] || 0)+
      parseFloat(data['modelSize']['TransportLength'] || 0);


     data['modelName'].includes('CSZE')  ? el_height = Number(el_height.toFixed(0)) : 0
     data['modelName'].includes('CSCC')  ? el_height = Number(el_height.toFixed(1)) :     el_height    = el_height

      console.log(data['modelName'],Number(el_height))
      El_elevator = All_elevator.filter(function(f) { return (f['model']).replace(' ', '').includes(data['modelName']) && f['height']==el_height})[0]
      console.log(El_elevator)
      if(El_elevator == undefined){
        BadToast(I18N.t('checkNumber'))

        return
      }
      document.getElementById('BlockChoiceMachine').style.display = 'flex'
      document.getElementById(`buttonNewCard__elevator`).style.display = 'flex'

      document.getElementById('Select_elevator').style.display = 'none'
      
      document.getElementById('buttonNewcheckLink').style.display = 'none'
      document.getElementById('buttonNewcheck').style.display = 'none'

      document.getElementById('ChoiceMachine').innerText = El_elevator['name_print']
      
      changed_price_List['elevator'] == undefined ? changed_price_List['elevator'] = {} : 0
      
      changed_price_List['elevator'][El_elevator['id_row']] =  Number(data['modelPrice'])*Number(data['NDS'])
      SaveChangePrice()
      data_CP['additional_info']['id_json'] == undefined ?  data_CP['additional_info']['id_json'] = {} :0
      data_CP['additional_info']['id_json'][El_elevator['id_row']] = id_deal
      addNewCard('buttonNewCard__elevator')
      GoodToast(I18N.t('elevatorAdded'))

    },
    error: function (error) {
      BadToast(I18N.t('checkNumber'))
    }
  }) 

}