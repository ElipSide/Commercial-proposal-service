
var dropArea 
var droppedContent

var UserData, lastmanagerInvoice, agreement_signed, invoice_sent, contract_ready
// const chars = document.getElementById('chars');

var mask
// заполняет поля данными из бд
async function InsertData(){

  document.getElementById('mask-inn-organization').value = check_info['inn']
  document.getElementById('AdresUser').value = check_info['address']
  document.getElementById('UserData_inputNumber').value = check_info['phone_number']

  if(User_Info['access_level']=='manager'){  
    var element = document.getElementById('telephoneManag');
  }else{
    var element = document.getElementById('UserData_inputNumber');
  }
  var maskOptions = {
    mask: '+{7}(000)000-00-00',
    lazy: false,  // make placeholder always visible
    placeholderChar: '#',     // defaults to '_'
  };
  mask = IMask(element, maskOptions)
  document.getElementById('emailUser').value = check_info['email']
  document.getElementById('mask-bik').value = check_info['bic']

  if(User_Info['access_level']=='manager'){  

    document.getElementById('companyManag').value = User_Info['company']
    document.getElementById('emailManag').value= User_Info['mail']
    document.getElementById('manag_SecondName').value= User_Info['middle_name']
    document.getElementById('manag_FirstName').value= User_Info['name']
    document.getElementById('telephoneManag').value= User_Info['phone_number']

    document.getElementById('telephone').innerText = mask.value
    document.getElementById('telephone').href = `tel:${mask.unmaskedValue}`
    element.click()
    document.getElementById('manag_SernameName').value= User_Info['surname']
    document.getElementById('manag_description').value= User_Info['description']
    document.getElementById('manag_post').value= User_Info['job_title']
    User_Info['description']!=''? document.getElementById('introduction').innerText = User_Info['description'] :0
    document.getElementById('manag_id_erp').value= User_Info['id_erp']
    Comp_shortname.innerText = check_info['organization_shortname']
  }

  document.getElementById('mask-account').value = check_info['checking_account']
  document.getElementById('SignerBlock').children[1].children[0].value = check_info['first_name']
  document.getElementById('SignerBlock').children[0].children[0].value = check_info['second_name'] 
  document.getElementById('SignerBlock').children[2].children[0].value = check_info['surname']
  document.getElementById('SignerBlock').children[3].children[0].value = check_info['position_user']
  document.getElementById('SelectProxy').value = check_info['acts_basis']
  document.getElementById('textareaValid').value = check_info['number_proxy']

  UserValid()
  CheckCompany()
  Checkcheck()
  CheckSigner()
}

// обновление данных в кп
function Update_KP(){
    number_proxy = String( document.getElementById('textareaValid').value) ==""? '':String( document.getElementById('textareaValid').value)

    if(User_Info['access_level']=='manager'){  
      User_Info= {
        'access_level': User_Info['access_level'],
        'company':  String(document.getElementById('companyManag').value) ,
        'data_reg': User_Info['data_reg'],
        'id_tg': ID_USER ,
        'language': "ru",
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
    }
    else{
      User_Info= {
        'access_level': User_Info['access_level'],
        'company': "",
        'data_reg': User_Info['data_reg'],
        'id_tg': ID_USER ,
        'language': "ru",
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
      "number_proxy":number_proxy,
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
      },
      error: function (error) {
        Error_Message(`Update_check_info error ${ID_USER}\n${error}`)
      }
  })  

    
}
// Сбор данных и создание договора
function GetAgreement(){
  CheckCompany()
  Checkcheck()
  CheckSigner()
  var price_listkp =[]
  var Parent = document.getElementById('blockTable')

  for (var n = 3; n < Parent.children.length; n++) {
    price_listkp.push({
      'name':Number(Parent.children[n].children[1].id.split('__')[2]),
      'price': Number((Number(Parent.children[n].children[4].innerText)/Number(Parent.children[n].children[3].children[0].value)).toFixed(1)),
      'type':Parent.children[n].children[1].id.split('__')[1]
    })
  }
  let Oneprovider_list = new Set();
  for (const group_key in data_CP['group_info']) {
    const group = data_CP['group_info'][group_key];
    for (const id_el_str in group) {
      var  id_el = Number(id_el_str);
      switch (group_key) {

        case 'Service':
          const El_Sieve = All_Service.find(f => f['id_row'] === id_el);
          if (El_Sieve) Oneprovider_list.add(El_Sieve['id_provider']);
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
      console.log('Manager_Csort')
      DataList= data
    }
    else{// договора для остальных
      data = Manager_Other(Oneprovider_list, price_listkp)
      console.log('Manager_Other')
      DataList= data
      console.log(DataList)
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
          case 'Service':
            El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el })[0]
            break;
          case 'attendance':
            El_item = All_attendance.filter(function(f) { return  f['id_row'] === id_el})[0]
            ads = "ads"
            break;
          
        }
          
        console.log(El_item)
        sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))
        const itemNamePrint = El_item['name_print'] || El_item['name'];

        if(El_item!= undefined){
          ListCheck_Agreement.push({
              'name': El_item['name'],
              'name_print': itemNamePrint,

              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': sum,
              'id': `deleteRow__Service__${el['id_row']}`,
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
  data['Chat_id'] =  ID_USER
  data['UserName'] = UserName
  data['page'] ='Service'
  if(User_Info['access_level']=='manager'){  
    data['Id_manager'] =  ID_USER
    data['client'] = false
  }
  else{
    data['Id_manager'] =  ''
    data['client'] = true
  }

  data['date'] =  List_CP['creation_date']
  data['client'] = false
  data['additional_info'] = data_CP['additional_info']

  DataList.push(data)
    if(User_Info['access_level']=='manager'){  
      DataList = DataList.reverse();

    }else{
      if(ID_provider == 3){ // договора для сисорта
          data = Manager_Csort(Oneprovider_list, price_listkp)
          console.log('Manager_Csort')
          DataList.push(...data);
          // DataList= data
        }
    }
  

  GoodToast('Пришлем договор в течение минуты')
  formData = JSON.stringify( DataList);
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
  DataList = []
  for (var n = 0; n <= Oneprovider_list.length-1;n++){
    
    provider = Oneprovider_list[n]
    if(provider==ID_provider){continue}
    var ListCheck_Agreement = []
    var Sum_ListCheck = 0
    for (const group_key in data_CP['group_info']) {
      const group = data_CP['group_info'][group_key];
      for (const id_el_str in group) {
        const id_el = Number(id_el_str);
        let count  = group[id_el_str]
        let El_item = []
        switch (group_key) {
          case 'Service':
            El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el && f['id_provider'] == provider})[0]
            break;
        }
        sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))

        if(El_item!= undefined){
          ListCheck_Agreement.push({
              'name': El_item['name'],
              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': sum,
              'id': `deleteRow__Service__${el['id_row']}`,
              "id_erp": El_item['id_erp']
          })
          Sum_ListCheck+=sum
        }
      }
    }
    data = ReturnDataCompany(ID_provider, provider, ListCheck_Agreement)
    Preambula_Buy = List_Provider.filter(function(f) { return f['id'] == 3})[0]['preamble_buy']
    Preambula_Sell = List_Provider.filter(function(f) { return f['id'] == provider})[0]['preamble_sell']
    data['Preambula'] = `${Preambula_Buy} и ${Preambula_Sell}`
    data['buyer']['user_id'] = ID_USER
    data['NameFile'] = data['seller']['organization_shortname'].replace(/"/g, '');
    data['id_provider'] = ID_provider
    data['key'] = key
    data['sum'] =  Sum_ListCheck
    data['Chat_id'] =  List_Provider.filter(function(f) { return f['id'] == provider})[0]['chat_id']
    DataList.push(data)
  }
  return DataList
}
// Сбор данных и для создания договора менеджерами кроме менеджеров сисорта
function Manager_Other(Oneprovider_list, price_listkp){
  var DataList = []
  for (var n = 0; n <= Oneprovider_list.length-1;n++){
    provider = Oneprovider_list[n]
    if(provider==ID_provider ){continue}
    var ListCheck_Agreement = []
    var Sum_ListCheck = 0
    for (const group_key in data_CP['group_info']) {
      const group = data_CP['group_info'][group_key];
      for (const id_el_str in group) {
        const id_el = Number(id_el_str);
        let count  = group[id_el_str]
        let El_item = []
        switch (group_key) {
          case 'Service':
            El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el && f['id_provider'] != ID_provider})[0]
            break;
        }
        sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))
        if(El_item!= undefined){
          ListCheck_Agreement.push({
              'name': El_item['name'],
              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': sum,
              'id': `deleteRow__compressor__${el['id_row']}`,
              "id_erp": El_item['id_erp']
          })
          Sum_ListCheck+=sum
        }
      }
    }
   
  }
  if(ListCheck_Agreement == undefined){ return DataList}
  data = ReturnDataCompany(ID_provider, 3, ListCheck_Agreement)
  Preambula_Buy = List_Provider.filter(function(f) { return f['id'] == ID_provider})[0]['preamble_buy']
  Preambula_Sell = List_Provider.filter(function(f) { return f['id'] == 3})[0]['preamble_sell']
  data['Preambula'] = `${Preambula_Buy} и ${Preambula_Sell}`
  data['buyer']['user_id'] = ID_USER
  data['NameFile'] = data['seller']['organization_shortname'].replace(/"/g, '');
  data['id_provider'] = ID_provider
  data['key'] = key
  data['sum'] =  Sum_ListCheck
  data['Chat_id'] =  List_Provider.filter(function(f) { return f['id'] == 3})[0]['chat_id']
  DataList.push(data)
  data = Csort_agrement(Oneprovider_list, price_listkp)
  DataList.push(...data);
  return DataList
}
function Csort_agrement(Oneprovider_list, price_listkp){
  var DataList = []
  for (var n = 0; n <= Oneprovider_list.length-1;n++){
    var ListCheck_Agreement = []
    var Sum_ListCheck = 0
    provider = Oneprovider_list[n]
    if(provider==ID_provider || provider==3){continue}
    console.log(provider)
    for (const group_key in data_CP['group_info']) {
      const group = data_CP['group_info'][group_key];
      for (const id_el_str in group) {
        const id_el = Number(id_el_str);
        let count  = group[id_el_str]
        let El_item = []
        switch (group_key) {
          case 'Service':
            El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el && f['id_provider'] == provider})[0]
            break;
        }
        sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))
        if(El_item!= undefined){
          ListCheck_Agreement.push({
              'name': El_item['name'],
              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': sum,
              'id': `deleteRow__compressor__${el['id_row']}`,
              "id_erp": El_item['id_erp']
          })
          Sum_ListCheck+=sum
        }
      }
    }
    // console.log(provider,ListCheck_Agreement)
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
    console.log(provider, data)
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
        case 'Service':
          El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
      }
      sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))

      if(El_item!= undefined){
        ListCheck_Agreement.push({
            'name': El_item['name'],
            'count' : count,
            'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
            'sum': sum,
            'id': `deleteRow__Service__${el['id_row']}`,
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
    BadToast('Заполните поля Компания и Счет')
    return
  }
  var price_listkp =[]
  var Parent = document.getElementById('blockTable')
  for (var n = 3; n < Parent.children.length; n++) {
    price_listkp.push({
      'name':Number(Parent.children[n].children[1].id.split('__')[2]),
      'price': Number((Number(Parent.children[n].children[4].innerText)/Number(Parent.children[n].children[3].children[0].value)).toFixed(1)),
      'type':Parent.children[n].children[1].id.split('__')[1]
    })
  } 
  let Oneprovider_list = new Set();
  for (const group_key in data_CP['group_info']) {
    const group = data_CP['group_info'][group_key];
    for (const id_el_str in group) {
      var  id_el = Number(id_el_str);
      switch (group_key) {
        case 'Service':
          const El_Sieve = All_Service.find(f => f['id_row'] === id_el);
          if (El_Sieve) Oneprovider_list.add(El_Sieve['id_provider']);
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
        case 'Service':
          El_item = All_Service.filter(function(f) { return  f['id_row'] === id_el})[0]
          break;
        case 'attendance':
          El_item = All_attendance.filter(function(f) { return  f['id_row'] === id_el})[0]
          ads = "ads"
          break;
      }
      sum = Number((price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count).toFixed(1))
      if(El_item!= undefined){
        const itemNamePrint = El_item['name_print'] || El_item['name'];

        ListCheck_Agreement.push({
            'name': El_item['name'],
            'name_print': itemNamePrint,
            'count' : count,
            'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
            'sum': sum,
            'id': `deleteRow__Service__${el['id_row']}`,
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
  data['sum'] =  Price_KP
  data['Chat_id'] =  ID_USER
  data['date'] =  List_CP['creation_date']
  data['UserName'] = UserName
  data['page'] ='Service'
  if(User_Info['access_level']=='manager'){  
    data['client'] = false
    data['Id_manager'] =  ID_USER
  }else{
    data['client'] = true
    data['Id_manager'] =  List_CP['manager_id_tg']
    if(ID_provider == 3){ // договора для сисорта
      data = Manager_Csort(Oneprovider_list, price_listkp)
      console.log('Manager_Csort')
      DataList.push(...data);
      // DataList= data
    }
  }
  data['additional_info'] = data_CP['additional_info']

  DataList.push(data)
  GoodToast('Пришлем счет в течение минуты')
  formData = JSON.stringify( DataList);
  $.ajax({
    type: 'post',
    url: '/off_bot/API/Sieve_GetCheck',
    data: formData,
    processData: false,
    contentType: false,
    async: true,
    success: function(data){
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
      CreateIn1сErp = true
    }else{
      CreateIn1сErp = false
    }
  data={
    'List':ListCheck,
    'CreateIn1сErp': true,
    'CategoryId':21,
    'number':'1',
    'nds':'включает',
    'id_erp_manager':User_Info['id_erp'],
    'FIO_manager':`${User_Info['name']} ${User_Info['middle_name']}`,
    'terms_payment': '100% предоплата',
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
  return data
}
// созданиме словаря с данными компании для создания договора/счета
function ReturnDataCompany(id_prov,id_seller, infoList){
  Update_KP()
  console.log(infoList)
  ListCheck = ReturnListCheck(infoList)
  data={
    'List':ListCheck,
    'number':'1',
    'nds':'включает',
    'id_erp_manager':User_Info['id_erp'],
    'FIO_manager':`${User_Info['name']} ${User_Info['middle_name']}`,
    'terms_payment': '100% предоплата',
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
          document.getElementById('SignerBlock').children[2].children[0].value = data['management']['name'].split(' ')[2]
          document.getElementById('SignerBlock').children[3].children[0].value = data['management']['post']
        }
        else{
          document.getElementById('SignerBlock').children[0].children[0].value = data['fio']['surname'] 
          document.getElementById('SignerBlock').children[1].children[0].value = data['fio']['name'] 
          document.getElementById('SignerBlock').children[2].children[0].value = data['fio']['patronymic'] 
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

//  Создание пдф и отправка пользователю
function SavePDF(){
    GoodToast('Пришлем КП в течение минуты')
    document.getElementById('GetKP_button').style.display = 'none'
    //height =  (document.getElementById('mainBlock').clientHeight * 0.012).toFixed(0)
    $.ajax({
      url:`/off_bot/API/Sieve_SavePDF/${ID_USER}/${key}`,
//${height}`,
      type: 'get',
      success: function (data) {
        GetMessageKP('Обновленное КП',``)
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
            GoodToast('Фотография успешно загружена')
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



