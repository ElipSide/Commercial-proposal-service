var TypeMAchine = {
  'sep_machine': '1',
  'photo_sorter': '2',
  'Sieve': '3',
  'compressor': '4',
  'extra_equipment': '5',
  'service': '6',
  'elevator': '7',
  'Pneumatic_feed':'8',
  'laboratory_equipment':'9'
}
var ArrMachine = {}, ListMAchine = {}
ID_provider = 3

var Deal_id =0
// Получение значений юзера по id_tg
function getUserInfo(){

  $.ajax({
      url: `/off_bot/API/getUserInfo/${ID_USER}`,
      type: 'get',
      success: function (data) {
          User_Info = data['user'][0]
          UserName = User_Info['login']
            // User_Info['access_level']='client'
          data['check_info'] != null ? (check_info= data['check_info'][0],InsertData()): ( checkinfo())

          if(User_Info['access_level']=='manager'){  
            if ( User_Info['company'] == '') {
                OpenManagerInfo()
            }
            if(User_Info['phone_number'][0]==8){
                User_Info['phone_number'] = User_Info['phone_number'].slice('1')
            }
            UpdateInfo_manager()
          }
          getKP_info()
      },
      error: function (error) {
        Error_Message(`getUserInfo error ${ID_USER}\n${error}`)
      }
  });
}

if(document.getElementById('address_user')!= undefined){$("#address_user").suggestions({
  token: "5c9a582c4549c1b027e0efed9b369721120e724c",
  type: "ADDRESS",
  /* Вызывается, когда пользователь выбирает одну из подсказок */
  onSelect: function(suggestion) {
      region = suggestion.data.region_with_type
  }
});}

// Закрытие блока ввода личной информации
function UpdateInfo_manager(){
  document.getElementById('company').innerText = User_Info['company']
  document.getElementById('mail').innerText= User_Info['mail']
  document.getElementById('FIO').innerText = `${User_Info['middle_name']} ${User_Info['name']}`
  document.getElementById('telephone').innerText = document.getElementById('telephoneManag').value
  document.getElementById('telephone').href = `tel:${document.getElementById('telephoneManag').value}`
  User_Info['photo'] != '' && User_Info['photo'] != null ? document.getElementById('BlockmanagerPhoto').src = `/off_bot${User_Info['photo']}` :0
  document.getElementById('post').innerText =User_Info['job_title']
  User_Info['description']!=''? (document.getElementById('introduction').innerText = User_Info['description'], document.getElementById('clientName').innerText = 'Уважаемый Клиент'):0
  managerInfoBlock.style.display = 'flex'
}
// Открытие блока ввода личной информации
function OpenManagerInfo() {

    Telegram.WebApp.offEvent('mainButtonClicked', openAD);
    Telegram.WebApp.offEvent('mainButtonClicked', openUserInfo);
    Telegram.WebApp.offEvent('mainButtonClicked', CloseManagerInfo);

    tg.MainButton.text = I18N.t('save');
    Telegram.WebApp.onEvent('mainButtonClicked', CloseManagerInfo);
    tg.MainButton.show();

    ListChange.style.display = 'flex';
    mainBlock.style.display = 'none';
}


// создание пустого списка для сохранения данных кп и его запись в бд
async function checkinfo() {
  try {
    const response = await fetch('/off_bot/API/create_check_info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const check_info = await response.json();

    check_info.id_tg = ID_USER; // Добавляем ID пользователя
    write_Check_info(check_info);
    
  } catch (error) {
    Error_Message(`checkinfo error: ${error}`);
  }
}

// запись нового кп с базу данных
function write_Check_info(check_info){
  formData = JSON.stringify({'check_info':check_info});
  $.ajax({
    url: '/off_bot/API/test',
    type: 'POST',
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
      console.log('обновили данные')
    },
    error: function (error) {
      // Error_Message(`writeCheckInfo error ${ID_USER}\n${error}`)
    }
  })
}


function extractDealId(url) {
  const match = url.match(/\/crm\/deal\/details\/(\d+)\/?/);
  return match ? match[1] : null;
}
 var Togl_company = true
// Получение данных кп по ключу
function getKP_info(){
  $.ajax({
      url: `/off_bot/API/getKPInfo/${key}`,
      type: 'get',
      success: function (data) {
          List_CP = data['List'][0]
          List_CP['creation_date'] = List_CP['creation_date'].split('T')[0]
          var date = new Date(List_CP['creation_date']);
          date.setDate(date.getDate() + 3);
          lastDay =date.toISOString().split('T')[0];
          List_CP['manager_id_tg'] = ID_USER
          if(data['createKP'][0]['additional_info']['link_deal']== undefined && Deal_id!=0){
            data['createKP'][0]['additional_info']['link_deal'] = `https://csort24.bitrix24.ru/crm/deal/details/${Deal_id}/`
            Togl_company = false
          }
          if( data['createKP'][0]['additional_info']['link_deal']!=undefined){
            Deal_id = extractDealId(data['createKP'][0]['additional_info']['link_deal']);
            download_Bitrix.children[0].innerText = 'Обновить сделку'

          }

          data_CP = structuredClone(data['createKP'][0]);
          if(pages =='Separator' || pages =='Sorting'){
            saved_data_CP = structuredClone(data['createKP'][0]);
          }
          if(document.getElementById('deal_bitrix_button')!= null){
            deal_bitrix_button.style.display = data_CP['additional_info']['link_deal'] !=undefined? 'flex': 'none'

          }

          data['changed_price_List'] == null  ? changed_price_List = {}: changed_price_List = data['changed_price_List'][0]['List']
          data['changed_sale_List'] == null  ? changed_sale_List = {}: changed_sale_List = data['changed_sale_List'][0]['List']
          if(pages != 'Separator' && pages !='Sorting'){
            if(User_Info['access_level']=='manager'){  
              data_CP['sale']!=null? document.getElementById('discount_input').value = data_CP['sale']:0
            }
            else{
              data_CP['sale'] = 0
              document.getElementById('discount_input').value =data_CP['sale']
            }
            getProvider_list()
              UpdateCPlist(data_CP, List_CP, 'offer')

          }
         
            // MainButton_func()
            // if(data_CP['price'] !=0){
            //     tg.MainButton.text = I18N.t('getAgreement'); //изменяем текст кнопки 
            //     Telegram.WebApp.onEvent('mainButtonClicked', openUserInfo)
            // }else{
            //     tg.MainButton.text = I18N.t('addProduct'); //изменяем текст кнопки 
            //     Telegram.WebApp.onEvent('mainButtonClicked', openAD)
            // }

          
      },
      error: function (error) {
        Error_Message(`getKPInfo error ${ID_USER}\n${error}`)
      }
  });
}
// Получение данных о поставщиках
function getProvider_list() {
  $.ajax({
      url: `/off_bot/API/getProviderData`,
      type: 'get',
      success: function (data) {
        List_Provider = data['provider'];

          if(User_Info['access_level']=='manager'){  
            let Parent = document.getElementById('companyManag');
            for (let n = Parent.children.length - 1; n >= 1; n--) {
                Parent.children[n].remove();
            }
            if(User_Info['company']!=''){
                ID_provider = List_Provider.filter(function(f) {return f['organization_shortname'] == User_Info['company']})[0]['id'];
            }
            for (let i = 0; i < List_Provider.length; i++) { 
                let el_name = List_Provider[i].organization_shortname;
                let el_id = List_Provider[i].organization_shortname;
                let TegClone = Parent.children[0].cloneNode(true);
                TegClone.value = el_id;
                TegClone.innerText = el_name;
                if(List_Provider[i].id==4 && ID_provider==3){TegClone.disabled = true;}
                else if(List_Provider[i].id==3 && ID_provider==4){TegClone.disabled = true;}
                else{
                                  TegClone.disabled = false;

                }
                // if(List_Provider[i].id!=4){TegClone.disabled = false;}
                Parent.appendChild(TegClone);
            }
            if(User_Info['company']!=''){
                document.getElementById('companyManag').value = User_Info['company'];
            }}


          getProd_list();
      },
      error: function (error) {
        Error_Message(`getProviderData error ${ID_USER}\n${error}`)
      }
  });
}

// получение данных о Доставке, Гарантии, Способах оплаты исходя из выбранной компании в профиле у пользователя

function getConditions_list(){

  $.ajax({
      url: `/off_bot/API/getConditionsData/${lang}`,
      type: 'get',
      success: function (data) {
        All_warranty=data['warranty']
        All_delivery_terms= data['delivery_terms']
        All_payment_method = data['payment_method']
        All_parametrs = data['dop_info']
        StartClone()
        getcounterparty_list()
          if(new URL(href).searchParams.get('number_calk')== null){
            const element = document.querySelector('.gifLoad');
            element.classList.add('hidden');
            element.addEventListener('transitionend', function() {
              if (element.classList.contains('hidden')) {
                element.style.display = 'none';
                  tg.MainButton.show() 
              }
            });
          }
        },
        error: function (error) {
          Error_Message(`getСonditionsData error ${ID_USER}\n${error}`)
        }
  });
}
//  Получение списка
async function getcounterparty_list(){
  $.ajax({
      url: `/off_bot/API/getcounterparty`,
      type: 'get',
      success: function (data) {
        All_counterparty = data['counterparty']
        Deal_id!='0'? PostAjax_bitrix_company() :0
      },
      error: function (error) {
        Error_Message(`getcounterparty error ${ID_USER}\n${error}`)
      }
  });
}

let dubl_result  = {}, dubl_machine = []
//  отмена изменения состава кп
function CancelChanges(){
  result = structuredClone(dubl_result)
  machine = dubl_machine
  var Parent = document.getElementById('blockTable')
  for (var n = Parent.children.length-1; n >= 3; n--) {Parent.children[n].remove()}
  StartClone()
  document.getElementById('imgChange').src = 'static/img/change.png'
  document.getElementById('imgChangeCancel').style.display = 'none'
}
// изменение количества выбранной строки
function unloadCountPlus(){
  quantityBlock.value =  Number(quantityBlock.value) + 1
}
// изменение количества выбранной строки
function unloadCountMinus(){
  if(Number(quantityBlock.value) ==1){
      BadToast(I18N.t('qtyMinOne'))
      return
  }
  quantityBlock.value =  Number(quantityBlock.value) - 1
}
// Создание списка компаний для поиска
function cloneSearch(Arr_into){
  ClearSearchBlock()
  var Parent = document.getElementById('SearchEl_scrollBlock').children[0]
  for (var i = 0; i < Arr_into.length; i++) {
      let TegClone = Parent.children[0] .cloneNode(true)
      TegClone.style.display = 'flex'
      TegClone.id  = `El_scrollBlock_${Arr_into[i]['id_row']}`
      TegClone.children[0].children[0].innerText = Arr_into[i]['name']
      TegClone.children[1].children[0].innerText = Arr_into[i]['region']
      TegClone.children[2].children[0].innerText = `ИНН: ${Arr_into[i]['inn']}`
      Parent.appendChild(TegClone);
  }
}
// Удаление списка компаний для поиска
function ClearSearchBlock(){
  var Parent = document.getElementById('SearchEl_scrollBlock').children[0]
  for (var n = Parent.children.length-1; n >= 1; n--) {Parent.children[n].remove()}
}
// запуск
function StartSearch(){
  text = document.getElementById('Search_el').value.toLowerCase()
  Arr_into = All_counterparty.filter(function(f) { return  f['name'].toLowerCase().includes(text)})
  cloneSearch(Arr_into)
}


function addcounterparty(){
  Search_block.style.display = 'none'
  UserInfo_Block.style.display = 'flex'
  // if(Choice_counter!=''){
  //     insert_dataEL(Choice_counter)
  // }
}

var Choice_counter = ''
function Choice_SearchEl(id){
    var Parent = document.getElementById('SearchEl_scrollBlock').children[0]
    for (var n = Parent.children.length-1; n >= 1; n--) {
        if(Parent.children[n].id == id){
            Parent.children[n].style.boxShadow == '' ? (Parent.children[n].style.boxShadow = 'rgba(34, 60, 80, 0.2) 0px 0px 10px 2px inset',Choicecounter(id) ) :  (Parent.children[n].style.boxShadow = '', Choice_counter = '')
        }
        else{
            Parent.children[n].style.boxShadow = '' 
        }
    }
}

function Choicecounter(id){
  console.log(id)
      $.ajax({
        url: `/off_bot/API/Id_counterparty/${id.split('_')[2]}`,
        type: 'get',
        success: function (data) {
          Choice_counter = data['counterparty'][0]
          insert_dataEL(Choice_counter)
          },
          error: function (error) {
            Error_Message(`Id_counterparty error ${ID_USER}\n${error}`)
          }
      });
    }

function Check_counterparty(){
  includes_counter = All_counterparty.filter(function(f) { return  f['inn'] == check_info['inn']}).length != [] 
  if(includes_counter){return}
  data = {
          "name": check_info['organization_shortname'],
          "orgn_ogrnip": check_info['ogrn'],
          "inn": check_info['inn'],
          "kpp": check_info['kpp'],
          "address": check_info['address'],
          "region":check_info['address'].split(', ')[1],
          "phone_number":check_info['phone_number'] ,
          "email":check_info['email'] ,
          "bank": check_info['bank_info'],
          "correspondent_account":check_info['corporate_account'] ,
          "bic": check_info['bic'],
          "surname": check_info['surname'],
          "first_name": check_info['first_name'],
          "patronymic":check_info['second_name'] ,
          "basis":check_info['acts_basis'] ,
          "number_proxy":check_info['number_proxy'],
          'checking_account' : check_info['checking_account']
      }
  formData = JSON.stringify( data);
  $.ajax({
    type: 'post',
    url: 'Save_NewCounter',
    data: formData,
    processData: false,
    contentType: false,
    async: true,
    success: function(data){
    },
    error: function (error) {
      Error_Message(`Save_NewCounter ${ID_USER}\n${error}`)
    } 
  }) 
}


function rebildPrice(id){
  var Parent = document.getElementById('blockTable')
  var AllPrice = 0
  for(var i = 3; i< Parent.children.length; i++){
      var number = Number(Parent.children[i].children[4].innerText)
      AllPrice += number
  }
  document.getElementById('Price_input').value = (Price_KP).toLocaleString()
  UpdateCPlist(data_CP, List_CP, 'offer')
}

CountSell = {"Payment":'',    "Delivery":'',"Warranty":'',}
// создание селектов и заполнение блоков Доставки, Гарантии и условий оплаты (ui)
function СonditionsData(){

  const result_id = Object.entries(data_CP['group_info'])
    .filter(([key, value]) => Object.keys(value).length > 0)
    .map(([key]) => TypeMAchine[key])
    .filter(Boolean) // На случай, если ключа нет в TypeMAchine
    .map(Number); // Преобразуем строки в числа
  var List_terms = All_warranty.filter(function(f) { return Number(f['id_provider']) == ID_provider})[0]

  Parent = document.getElementById('WarrantySelect')
  result_id.length == 0? List_terms_text = '': List_terms_text =`${List_terms['text']['text']}: `
  for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
  var Children = Parent.children[0]
  for(var i = 0; i< result_id.length; i++){
    if(List_terms['text'][result_id[i]] == undefined){continue}

    List_terms_text+=`${List_terms['text'][result_id[i]]},\n`
  }
  document.getElementById('textWarranty').innerText = List_terms_text
  CountSell['Warranty']=0

  Parent = document.getElementById('DeliveryTimeSelect')
  for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
  var Children = Parent.children[0]
  var List_terms = All_delivery_terms.filter(function(f) { return Number(f['id_provider']) == ID_provider})[0]
  List_terms_text = ''
  for(var i = 0; i< result_id.length; i++){
    if(List_terms['text'][result_id[i]] == undefined){continue}
    List_terms_text+=`${List_terms['text'][result_id[i]]}\n`
  }
  document.getElementById('textDeliveryTime').innerText = List_terms_text
  CountSell['Delivery'] =0

  Parent = document.getElementById('TermspaymentSelect')
  for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
  var Children = Parent.children[0]
  var List_terms = All_payment_method.filter(function(f) { return Number(f['id_provider']) == ID_provider})
  for(var i = 0; i< List_terms.length; i++){
      var Clone = Children.cloneNode(true)
      Clone.style.display = 'flex'
      Clone.value = List_terms[i].payment_distribution
      // document.getElementById('textPaymenTerms').innerText = List_terms[i].text
      Clone.innerText = List_terms[i].payment_distribution
      Parent.appendChild(Clone)
  }
    List_CP['payment_method']!=''?(document.getElementById('TermspaymentSelect').value = List_CP['payment_method']):document.getElementById('TermspaymentSelect').value  = I18N.t('prepayment100')
  Termsofpayment()
}
// Отправка сообщения в указанный чат
function SendMessage(data){
  var result 
  formData = JSON.stringify(data);
  $.ajax({
    type: 'POST',
    url: '/off_bot/API/SendMessage_ChatTo',
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
  },
  error: function (error) {
    Error_Message(`SendMessage_ChatTo error ${ID_USER}\n${error}`)
  }
  }) 
  return result
}
var Guarantee, Delivery_time ,terms_payment 
// открытые блока создания Счета/договора
async function openUserInfo(){
  Telegram.WebApp.offEvent('mainButtonClicked', openUserInfo);

  if(!hasNonEmptyDict(data_CP['group_info'])){
      BadToast(I18N.t('noItemsSelected'))
      return
  }
  Guarantee = WarrantySelect.value
  Delivery_time = DeliveryTimeSelect.value
  terms_payment = TermspaymentSelect.value
  await sleep(100)
  window. scrollTo(0, 0)
  mainBlock.style.display = 'none'
  UserInfo_Block.style.display = 'flex'
  tg.MainButton.text = "-"; //изменяем текст кнопки 
  tg.MainButton.color = "#ffffff"; //изменяем цвет бэкграунда кнопки
  tg.MainButton.hide()
  var BackButton = tg.BackButton;
  BackButton.show();
  Telegram.WebApp.onEvent('backButtonClicked', BackKP)
  UpdateCPlist(data_CP, List_CP, 'offer')
} 
// возврат из блока создания Счета/договора
function BackKP(){
    Telegram.WebApp.onEvent('mainButtonClicked', openUserInfo);

  mainBlock.style.display = 'flex'
  UserInfo_Block.style.display = 'none'
  tg.MainButton.text = I18N.t('getAgreement');
  tg.MainButton.textColor = "#fff"; //изменяем цвет текста кнопки
  tg.MainButton.color = "#e01818"; //изменяем цвет бэкграунда кнопки
  tg.MainButton.show();
  tg.MainButton.enable()
  var BackButton = tg.BackButton;
  BackButton.hide()
}



// отправка КП( пдф) если он уже был создан ранее 
// function SendContract(){
//   text = ''
//   dataUser={
//       INN: document.getElementById('mask-inn-organization').value,
//       Adres: document.getElementById('AdresUser').value,
//       Number: document.getElementById('UserData_inputNumber').value,
//       email: document.getElementById('emailUser').value,

//   }
//   formData = JSON.stringify({"ID_USER":ID_USER, "UserName":UserName, "Url": Url, "Date": date, "text":text});
//   $.ajax({
//     type: 'POST',
//     url: '/Sieve_SendPDF',
//     data: formData,
//     processData: false,
//     contentType: false,
//     success: function(data){
//   },
//   error: function (error) {
//     Error_Message(`Sieve_SendPDF error ${ID_USER}\n${error}`)
//   }
//   }) 

//   tg.MainButton.text = I18N.t('getAgreement');
//   tg.MainButton.show();
// }

// проверки заполнения инпутов 
function INNWrite(){
  lengthINN = document.getElementById('mask-inn-organization').value.length
  lengthINN !=10 && lengthINN != 12? document.getElementById('mask-inn-organization').style.borderColor = 'red':(document.getElementById('mask-inn-organization').style.borderColor = '#ccc',SearchInn())
  lengthINN==12? document.getElementById('SelectProxy').value = 'Доверенность' :'Устав'
  lengthINN==10? document.getElementById('SelectProxy').value = 'Свидетельство' :'Устав'
  UserValid()
  CheckCompany()
}
function UserValid(){
  if(document.getElementById('SelectProxy').value == 'Устав'){document.getElementById('NumberProxy').style.display = 'none', document.getElementById('textareaValid').value = '';return}
  document.getElementById('SelectProxy').value =='Свидетельство' ? (document.getElementById('NumberProxy').style.display = 'flex', document.getElementById('NumberProxy').children[0].placeholder='Введите номер и дату свидетельства' ):0
  document.getElementById('SelectProxy').value == 'Доверенность'? (document.getElementById('NumberProxy').style.display = 'flex', document.getElementById('NumberProxy').children[0].placeholder='Введите номер и дату доверенности' ):0
}
function accountWrite(){
  lengthINN = document.getElementById('mask-account').value.length
  lengthINN !=20 ? document.getElementById('mask-account').style.borderColor = 'red':document.getElementById('mask-account').style.borderColor = '#ccc'
}
function bicWrite(){
  lengthINN = document.getElementById('mask-bik').value.length
  lengthINN !=9 ? document.getElementById('mask-bik').style.borderColor = 'red':(document.getElementById('mask-bik').style.borderColor = '#ccc',SearchBic())
  Checkcheck()
}
function NumberWrite(){
  // lengthINN = document.getElementById('UserData_inputNumber').value.length
  document.getElementById('UserData_inputNumber').value == ''? document.getElementById('UserData_inputNumber').style.borderColor = 'red':(document.getElementById('UserData_inputNumber').style.borderColor = '#ccc')
}
function CheckCompany(){
  var ToglCompany = true
  lengthINN = document.getElementById('mask-inn-organization').value.length
  lengthINN !=10 && lengthINN != 12 && document.getElementById('mask-inn-organization').style.borderColor != '#ccc' ?ToglCompany=false :0
  document.getElementById('UserData_inputNumber').value != '' && document.getElementById('emailUser').value != '' ?0 :ToglCompany=false
  document.getElementById('AdresUser').value == '' && document.getElementById('AdresUser').style.borderColor != '#ccc' ?ToglCompany=false :0
  ToglCompany == true? ( document.getElementById('Name_CompanyBlock').style.backgroundColor = '#d2fed2',document.getElementById('Name_CompanyBlock').style.margin='5px 0px') :( document.getElementById('Name_CompanyBlock').style.backgroundColor = 'white',document.getElementById('Name_CompanyBlock').style.margin='0px 0px')
}
function Checkcheck(){
  var Toglcheck = true
  document.getElementById('mask-bik').value == '' && document.getElementById('mask-bik').style.borderColor != '#ccc' ? Toglcheck=false :0;
  document.getElementById('mask-account').value.length !=20 && document.getElementById('mask-account').style.borderColor != '#ccc' ? Toglcheck=false :0;
  Toglcheck == true? ( document.getElementById('Name_CheckBlock').style.backgroundColor = '#d2fed2',document.getElementById('Name_CheckBlock').style.margin='5px 0px') :(document.getElementById('Name_CheckBlock').style.backgroundColor = 'white',document.getElementById('Name_CheckBlock').style.margin='0px 0px')
}
function CheckSigner(){
  var Toglcheck = true
  document.getElementById('SignerBlock').children[6].style.display =='flex' && document.getElementById('SignerBlock').children[6].children[0].value == ''?Toglcheck = false :0
  for(var i =0; i<4; i++){
      document.getElementById('SignerBlock').children[i].children[0].value == '' ? Toglcheck = false :0
  }
  // document.getElementById('SignerBlock').children[5].style.display =='flex' && document.getElementById('SignerBlock').children[5].children[0].value == ''?Toglcheck = false :0
  Toglcheck == true? ( document.getElementById('Name_SignerBlock').style.backgroundColor = '#d2fed2',document.getElementById('Name_SignerBlock').style.margin='5px 0px') :( document.getElementById('Name_SignerBlock').style.backgroundColor = 'white', document.getElementById('Name_SignerBlock').style.margin='0px 0px')
}

// закрытие листа для добавления и обнуление данных 
function ClearBlock(parent){
  document.getElementById(parent).style.display = 'none'
  TegParent =  document.getElementById(parent).children[0]
  for (var n = TegParent.children.length-1; n >= 1; n--) {
      TegParent.children[n].remove()
  }
}

// запись нового кп
function writeNewCP(pages){
  $.ajax({
    type: 'POST',
    url: `/off_bot/API/Write_new_cp/${pages}/${ID_USER}/${new URL(href).searchParams.get('keyCP')}`,
    processData: false,
    contentType: false,
    success: function(data){
      data_CP = data.data_CP,
      List_CP = data.List_CP,
      key = data.key
      writeCPlist(data_CP, List_CP, pages)

    },
    error: function (error) {
      Error_Message(`writeCPlist error ${error}`)
    }
    })  


  
}  

// Функция сохранения цены ,обновление данных в базе данных
function     SaveChangePrice(){
  formData = JSON.stringify({'cp_key': key,'changed_price_List':changed_price_List});
  $.ajax({
    type: 'POST',
    url: `/off_bot/API/SaveChangePrice`,
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
     
    },
    error: function (error) {
      Error_Message(`writeCPlist error ${error}`)
    }
    })  
}

// Функция сохранения скидки ,обновление данных в базе данных
function SaveChangeSale(){
  formData = JSON.stringify({'cp_key': key,'changed_sale_List':changed_sale_List});
  $.ajax({
    type: 'POST',
    url: `/off_bot/API/SaveChangeSale`,
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
     
    },
    error: function (error) {
      Error_Message(`SaveChangeSale error ${error}`)
    }
    })  
}


async function writeCPlist(data_CP, List_CP, pages) {
  try {
    const response = await fetch(`/off_bot/API/Write_createdKP/${pages}/${ID_USER}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({createKP: data_CP, List: List_CP}),
    });
    
    
    if (pages === 'offer' || pages === 'Service') {
      const isLocal = window.location.href.includes('127.0.0.1');
      const baseUrl = isLocal ? 'http://127.0.0.1:8000' : 'https://csort-news.ru';
      window.location.href = `${baseUrl}/off_bot/${pages}/home?keyCP=${key}&tg_id=${ID_USER}&username=${UserName}&deal=${Deal_id}`;
    }
    
    return true;
  } catch (error) {
    console.error('Error:', error);
    Error_Message(`writeCPlist error ${error}`);
    return false;
  }
}



// обновление данных о КП/сервисном передложении в бд
function UpdateCPlist(data_CP, List_CP, pages){
  document.getElementById('nds')!= undefined ? data_CP['additional_info']['nds'] = document.getElementById('nds').value : 0
  save_CP = saved_data_CP==undefined ? data_CP: mergeGroupInfo(data_CP, saved_data_CP)

  formData = JSON.stringify({'createKP':save_CP, 'List': List_CP});
  $.ajax({
    type: 'POST',
    url: `/off_bot/API/Update_createdKP/${ID_USER}`,
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
      hrefPage =window.location.href.includes('127.0.0.1')== true ? 'http://127.0.0.1:8000/off_bot/offer/home': 'https://csort-news.ru/off_bot/offer/home'
      pages == 'Sorting' ? window.location.href =` ${hrefPage}?keyCP=${key}&tg_id=${ID_USER}&username=${UserName}&deal=${Deal_id}`  : 0
      pages == 'Separator' ? window.location.href =` ${hrefPage}?keyCP=${key}&tg_id=${ID_USER}&username=${UserName}&deal=${Deal_id}`  : 0
    },
    error: function (error) {
      Error_Message(`UpdateCPlist error ${error}`)
    }
  })  
}

function mergeGroupInfo(dict1, dict2) {
  const mergedGroupInfo = {};
  for (const key in dict1.group_info) {
      if (dict2.group_info.hasOwnProperty(key)) {
          if (typeof dict1.group_info[key] === "object" && typeof dict2.group_info[key] === "object") {
              mergedGroupInfo[key] = {};
              const subKeys = new Set([
                  ...Object.keys(dict1.group_info[key]),
                  ...Object.keys(dict2.group_info[key])
              ]);
              subKeys.forEach((subKey) => {
                  const value1 = dict1.group_info[key][subKey] || 0;
                  const value2 = dict2.group_info[key][subKey] || 0;
                  mergedGroupInfo[key][subKey] = value1 + value2;
              });
          } else {
              mergedGroupInfo[key] = dict1.group_info[key];
          }
      } else {
          mergedGroupInfo[key] = dict1.group_info[key];
      }
  }
  return {
      ...dict1,
      group_info: mergedGroupInfo
  };
}

function changeCountPlus(){
  changeBlock.value =  Number(changeBlock.value) + 1
}
function changeCountMinus(){
  if(Number(changeBlock.value) ==1){
      BadToast('Количество не может быть меньше одного')
      return
  }
  changeBlock.value =  Number(changeBlock.value) - 1
}
function getCount_list(){
  $.getJSON ($SCRIPT_ROOT + '/get_CountList', { //получаем json с сайта
  }, function (date) { //открываем функцию
      CountList = date
  })
}






function GoodToast(text){
  Toastify({
    text: text,
    duration: 1500,
    gravity: "top", // `top` or `bottom`
    position: "center", // `left`, `center` or `right`
    style: {
      background: "linear-gradient(to right, #00b09b, #96c93d)",
    },
  }).showToast();
}
function BadToast(text){
  Toastify({
    text: text,
    duration: 1500,
    gravity: "top", // `top` or `bottom`
    position: "center", // `left`, `center` or `right`
    style: {
        background: "linear-gradient(to right, #e3b2b2, #d74242)",
    },
  }).showToast();
}

function WarningToast(text){
Toastify({
  text: text,
  duration: 1500,
  gravity: "top", // `top` or `bottom`
  position: "center", // `left`, `center` or `right`
  style: {
      background: "linear-gradient(to right, 	#ffcc00, 	#ff9966)",
  },
}).showToast();
}

// сон для задежки 
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// отправка сообщения об ошибке 
function Error_Message(text){
  data = {'text':text,'chatID':ID_USER}
  formData = JSON.stringify(data);
  $.ajax({
    type: 'POST',
    url: '/off_bot/API/Error_KP',
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
  }
  }) 

}

// скролл к указанному блоку
function Scroll_startBlock(targetElement){
  targetElement.scrollIntoView({
      behavior: 'smooth', // Плавная прокрутка
      block: 'start'     // Скролл к началу элемента
  });
}

function Botton_calk(){
  const container = document.getElementById('buttonContainer');
  const button = document.getElementById('mainButtonCalk');
  const rect = button.getBoundingClientRect();
  container.style.top = `${rect.bottom + window.scrollY + 5}px`;
  container.classList.toggle('hidden');
}

// очистка данных списка 
function cleanDataExceptIdTg(data) {
  return Object.keys(data).reduce((cleanedData, key) => {
      cleanedData[key] = (key === "id_tg"  ||key === "lastmanager_invoice" )
          ? data[key] 
          : typeof data[key] === "string"
          ? ""
          : typeof data[key] === "boolean"
          ? false
          : typeof data[key] === "number"
          ? 0
          : data[key] instanceof Date
          ? null
          : null;
      return cleanedData;
  }, {});
}

// очистка данных в блоке ввода данных покупателя
function ClearRecognize_data(){
  check_info =  cleanDataExceptIdTg(check_info);
  document.getElementById('mask-inn-organization').value = ''
  document.getElementById('AdresUser').value = ''
  document.getElementById('UserData_inputNumber').value = ''
  document.getElementById('emailUser').value = ''
  document.getElementById('mask-bik').value = ''
  document.getElementById('mask-account').value = ''
  document.getElementById('SignerBlock').children[1].children[0].value = ''
  document.getElementById('SignerBlock').children[0].children[0].value = ''
  document.getElementById('SignerBlock').children[2].children[0].value = ''
  document.getElementById('SignerBlock').children[3].children[0].value = ''
  document.getElementById('SelectProxy').value = ''
  document.getElementById('textareaValid').value = ''
  document.getElementById('Comp_shortname').innerText = ''
  // GoodToast(I18N.t('dataCleared'))
  CheckCompany()
  Checkcheck()
  CheckSigner()
}

function Recognize_data(){
  document.getElementById("fileElem_Recognize").value = ''
  var el = document.getElementById("fileElem_Recognize");
  if (el) {
    el.click();
  }
}
var Togl_RecognizeFiles = false

// добавление фото/пдф/текстового файла для отправки и распознования на нем информации о клиенте
function RecognizeFiles(files_photo, id){
  Togl_RecognizeFiles = false
  var files_photo = document.getElementById(`fileElem_Recognize`).files
  TypeForm = new FormData();
  TypeForm.append(`file`, files_photo[0])
  formData = TypeForm;
  UserInfo_Block.style.filter = 'blur(2px)'
  UserInfo_Block.style.pointerEvents = 'none'
  LoopToast()
  $.ajax({
          type: 'POST',
          url: `/off_bot/API/RecognizeFiles/${ID_USER}`,
          data: formData,
          processData: false,
          contentType: false,
          success: function(data){
            if(data['result']== null){
              BadToast(I18N.t('chooseAnotherFile'))
              UserInfo_Block.style.filter = 'none'
              UserInfo_Block.style.pointerEvents = 'auto'
              Togl_RecognizeFiles = true
              return
            }
            Togl_RecognizeFiles = true

            insert_dataEL(data['result'][0])
            UserInfo_Block.style.filter = 'none'
            UserInfo_Block.style.pointerEvents = 'auto'
            GoodToast(I18N.t('doneThanks'))
          },
          error: function (error) {
            BadToast(I18N.t('chooseAnotherFile'))
            UserInfo_Block.style.filter = 'none'
            UserInfo_Block.style.pointerEvents = 'auto'
            Togl_RecognizeFiles = true
          } 
      })  
    
  
}
const waitingMessages = [
  I18N.t('wait1'),
  I18N.t('wait2'),
  I18N.t('wait3'),
  I18N.t('wait4'),
  I18N.t('wait5'),
  I18N.t('wait6'),
  I18N.t('wait7'),
  I18N.t('wait8'),
  I18N.t('wait9'),
  I18N.t('waitDone')
];


// функция выпадающих тостов для ожидания
async function LoopToast(){
  var loop = 0
  while (!Togl_RecognizeFiles){
    WarningToast(waitingMessages[loop])
    loop == 9 ? loop = 0: loop+=1
    await sleep(4000)

  }
}


function follow_link(id){
  if(id == 'elevator'){
    User_Info['access_level']=='manager' ?client_web = false : client_web= true
    hrefPage =window.location.href.includes('127.0.0.1')== true ? `http://127.0.0.1:5000/calc`: `https://csort-transport.ru/calc`
    window.location.href =` ${hrefPage}?id=telegram_folder&keyCP=${key}&tg_id=${ID_USER}&username=${UserName}&deal=${Deal_id}&client_web=${client_web}`
  }else{
    hrefPage =window.location.href.includes('127.0.0.1')== true ? `http://127.0.0.1:8000/off_bot/${id}/home`: `https://csort-news.ru/off_bot/${id}/home`
    window.location.href =` ${hrefPage}?keyCP=${key}&tg_id=${ID_USER}&username=${UserName}&deal=${Deal_id}`
  }
}


function openAD(){
  tg.MainButton.text = I18N.t('back'); //изменяем текст кнопки 
  tg.MainButton.textColor = "#5b6579"; //изменяем цвет текста кнопки
  tg.MainButton.color = "#f2f2f2"; //изменяем цвет бэкграунда кнопки
  Telegram.WebApp.offEvent('mainButtonClicked', openAD)
  Telegram.WebApp.offEvent('mainButtonClicked', openUserInfo)
  Telegram.WebApp.onEvent('mainButtonClicked', CloseInfo)
  windowProductAd.style.display = 'flex'
  // mainBlock.style.filter = 'blur(2px)'
  mainBlock.style.display = 'none'
  scroll_Product_search()
  document.getElementById('buttonNewCard').style.display = 'flex'

}
function hasNonEmptyValues(obj) {
    for (const key in obj) {
        if (Object.keys(obj[key]).length !== 0) {
            return true;
        }
    }
    return false;
}

function MainButton_func() {

    Telegram.WebApp.offEvent('mainButtonClicked', openAD);
    Telegram.WebApp.offEvent('mainButtonClicked', openUserInfo);
    Telegram.WebApp.offEvent('mainButtonClicked', CloseManagerInfo);

    if (new URL(href).searchParams.get('number_calk') != null) return;

    let toggle = hasNonEmptyValues(data_CP['group_info']);

    if (toggle) {
        tg.MainButton.text = I18N.t('getAgreement');
        Telegram.WebApp.onEvent('mainButtonClicked', openUserInfo);
        blockTable.style.display = 'flex';
        add_button.style.display = 'flex';
        results.style.display = 'flex';
    } else {
        tg.MainButton.text = I18N.t('addProduct');
        Telegram.WebApp.onEvent('mainButtonClicked', openAD);
        blockTable.style.display = 'none';
        add_button.style.display = 'none';
        results.style.display = 'none';
    }

    tg.MainButton.textColor = "#fff";
    tg.MainButton.color = "#e01818";
    tg.MainButton.show();
}


togl_CloseInfo = false
function CloseInfo(){

  Telegram.WebApp.offEvent('mainButtonClicked', CloseInfo)

  togl_CloseInfo == false? MainButton_func():0
  togl_CloseInfo = false
  // Price_KP == 0? (Telegram.WebApp.onEvent('mainButtonClicked', openAD), tg.MainButton.text = I18N.t('addProduct')): (Telegram.WebApp.onEvent('mainButtonClicked', openUserInfo), tg.MainButton.text = I18N.t('getAgreement'))
  addType = ''
  quantityBlock.value = 1
  ClearBlock('Separ_configuration')
  ClearBlock('SelectSieve')
  ClearBlock('Select_provider')
  document.getElementById('search_subtitle_nomenclature').children[0].children[0].id  = 'BlockBackInfo'
  document.getElementById('BlockAddRow').children[1].children[0].id  = 'buttonNewCard'
  search_filterBlock.style.display = 'flex'
  BlockAddRow.style.display = 'none'
  windowProductAd.style.display ='none'
  // mainBlock.style.filter = 'none'
  mainBlock.style.display = 'flex'

  // tg.MainButton.hide()
  Scroll_startBlock(document.getElementById('blockTable'))
}

ActsOnTheBasis = {
  'Устав':'Устава',
  'Свидетельство':'Свидетельства',
  'Доверенность':'Доверенности'
}
// открытие расширенного списка данных
function openFullList(){



  if(Name_CheckBlock.style.backgroundColor =='white' || Name_CompanyBlock.style.backgroundColor  =='white' || Name_SignerBlock.style.backgroundColor =='white'){
    BadToast(I18N.t('fillCompanyInvoiceSigner'))
    return
  }

  Update_KP()
  // infodata = ReturnData()
  dataBuyer = check_info
  paymentyBlock.value = document.getElementById('textPaymenTerms').innerText
  deliveryBlock.value = document.getElementById('textDeliveryTime').innerText
  WarrantyBlock.value = document.getElementById('textWarranty').innerText
  if(document.getElementById('address_user')!= undefined){
    address_user.value = data_CP?.additional_info?.address_delivery || ''
  }
  dataSeller = List_Provider.filter(function(f) { return f['id'] == ID_provider})[0]
  buyerBlock = document.getElementById('buyerBlock').children
  // providerBlock  = document.getElementById('providerBlock').children
  dataSeller['index'] = Number(dataSeller['address'].split(',')[0])
  formData = JSON.stringify(
      {'text':[
      dataBuyer['first_name'],
      dataBuyer['surname'], 
      dataBuyer['position_user'],
      dataSeller['first_name'],
      dataSeller['surname'],
      dataSeller['position_user']
  ]});
  UserInfo_Block.style.filter = 'blur(2px)'
  UserInfo_Block.style.pointerEvents = 'none'

  $.ajax({
    type: 'post',
    url: 'Sieve_CaseChange',
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
      Telegram.WebApp.offEvent('mainButtonClicked', CloseInfo)
      Telegram.WebApp.offEvent('mainButtonClicked', openUserInfo);

      tg.MainButton.text = I18N.t('getContract');  
      tg.MainButton.textColor = "#fff";
      tg.MainButton.color = "#e01818"; 
      Telegram.WebApp.onEvent('mainButtonClicked', GetAgreement)
      tg.MainButton.show();

      dataSeller_second = dataSeller['second_name'].slice(-1) == 'а'? dataSeller['second_name']: `${dataSeller['second_name']}а`
      dataBuyer_second = String(dataBuyer['second_name']).slice(-1) == 'а'? dataBuyer['second_name']: `${dataBuyer['second_name']}а`

      UserInfo_Block.style.display = 'none'
      ListFullData.style.display = 'flex'
      Telegram.WebApp.offEvent('backButtonClicked', BackKP)
      Telegram.WebApp.onEvent('backButtonClicked', BackUserInfo)

      
      window.scroll(0, 0)
      BuyerNumberProxy = dataBuyer['number_proxy'] == ''? '': ` ${dataBuyer['number_proxy']}`
      SellerNumberProxy = dataBuyer['number_proxy'] == ''? '': ` ${dataSeller['number_proxy']}`

      textPream = `${dataBuyer['organization_fullname']}, далее именуемое «Покупатель», в лице ${data[2]} ${dataBuyer_second} ${data[0]} ${data[1]}, действующего на основании ${ActsOnTheBasis[dataBuyer['acts_basis']]}${BuyerNumberProxy}, с одной стороны, и ${dataSeller['organization_fullname']}, далее именуемое «Поставщик», в лице ${data[5]} ${dataSeller_second} ${data[3]} ${data[4]}, действующего на основании ${ActsOnTheBasis[dataSeller['acts_basis']]}${SellerNumberProxy}, с другой стороны, заключили настоящий договор о нижеследующем:`
      document.getElementById('preambulBlock').value = String(textPream)
      UserInfo_Block.style.filter = 'none'
      UserInfo_Block.style.pointerEvents = 'auto'

  },
  error: function (error) {
    // Error_Message(`Sieve_CaseChange error ${ID_USER}\n${error}`)
    BadToast(I18N.t('tryAgainError'))
    UserInfo_Block.style.filter = 'none'
    UserInfo_Block.style.pointerEvents = 'auto'

  }
  }) 
  buyerBlock[0].children[0].value = dataBuyer['organization_shortname']
  buyerBlock[2].children[0].value = dataBuyer['ogrn']
  buyerBlock[3].children[0].value = dataBuyer['inn']
  buyerBlock[4].children[0].value = dataBuyer['kpp']
  buyerBlock[5].children[0].value = dataBuyer['address']
  buyerBlock[6].children[0].value = dataBuyer['phone_number']
  buyerBlock[7].children[0].value = dataBuyer['email']
  buyerBlock[8].children[0].value = dataBuyer['checking_account']
  buyerBlock[9].children[0].value = dataBuyer['bank_info']
  buyerBlock[10].children[0].value = dataBuyer['corporate_account']
  buyerBlock[11].children[0].value = dataBuyer['bic']
 
}

function OpenSearch(){
  Telegram.WebApp.offEvent('backButtonClicked', BackKP)
  Telegram.WebApp.onEvent('backButtonClicked', addcounterparty)
  Search_block.style.display = 'flex'
  UserInfo_Block.style.display = 'none'
  cloneSearch(All_counterparty)

}
function BackUserInfo(){
  Telegram.WebApp.offEvent('backButtonClicked', BackUserInfo)
  Telegram.WebApp.onEvent('backButtonClicked', BackKP)
  UserInfo_Block.style.display = 'flex'
  ListFullData.style.display = 'none'
  tg.MainButton.hide();
  Telegram.WebApp.offEvent('mainButtonClicked', GetAgreement)
}


function discountAd(id){
  if(document.getElementById(id).value < 0 ){
    document.getElementById(id).value =0
    WarningToast(I18N.t('discountNegative'))
    return
  }

  if(document.getElementById(id).value > 40){
    document.getElementById(id).value =40
    WarningToast(I18N.t('discountLimit'))
    return
  }
  if(id == 'discount_input'){
    var Parent = document.getElementById('blockTable')
    for (var n = Parent.children.length-1; n >= 3; n--){Parent.children[n].remove()}
    StartClone()
  }
  else{
    var infoID = document.getElementById(id).parentNode.parentNode.parentNode.parentNode.children[2].id
    var ID_M = infoID.split('__')[2]
    var sale = Number(document.getElementById(id).value)
    var price = Number(document.getElementById('changeBlockPrice').value)
    document.getElementById('price_with_sale').innerText = (price - Number(((sale/100) * price).toFixed(1))).toLocaleString()
  }
}

function Blur_pointerEvent_on(Parent){
  document.getElementById(Parent).style.pointerEvents = 'none'
  document.getElementById(Parent).style.filter = 'blur(2px)'
}
function Blur_pointerEvent_off(Parent){
  document.getElementById(Parent).style.pointerEvents = 'auto'
  document.getElementById(Parent).style.filter = 'none'
}

function GettransportCalc(){
  hrefPage =window.location.href.includes('127.0.0.1')== true ? `http://127.0.0.1:5000/calc`: `https://csort-transport.ru/calc`
  window.location.href =` ${hrefPage}?id=telegram_folder&keyCP=${key}&tg_id=${ID_USER}&username=${UserName}&deal=${Deal_id}`
}

let saved_data_CP


function Sorted_extra_equipment(data){
  const sortedData = data.sort((a, b) => {
      const trayA = a.tray;
      const trayB = b.tray;
      // Если tray пустой или содержит "-", помещаем объект в конец
      if (!trayA || trayA === "-") return 1;
      if (!trayB || trayB === "-") return -1;
      // Если tray содержит несколько значений (через "|"), берем первое число
      const numA = parseInt(trayA.split("|")[0], 10);
      const numB = parseInt(trayB.split("|")[0], 10);
      return numA - numB;
  });
  return sortedData
}

function hasNonEmptyDict(data) {
    for (const key in data) {
        if (data[key] && typeof data[key] === 'object' && Object.keys(data[key]).length > 0) {
            return true;
        }
    }
    return false;
}


function OpenSettings(){
  tg.MainButton.hide()
  ListChange.style.display = 'flex'
  mainBlock.style.display = 'none'
}

function CloseSettings(){
    tg.MainButton.show() 
    Update_KP()
    ListChange.style.display = 'none'
    mainBlock.style.display = 'flex'
}

function copyToClipboard(element) {
    const textarea = document.createElement('textarea');
    textarea.value = element.textContent || element.innerText;
    textarea.style.position = 'fixed'; 
    document.body.appendChild(textarea);
    textarea.select();
    const successful = document.execCommand('copy');
    if (successful) {
        // Меняем текст на "Скопировано!" на короткое время
        const originalText = element.innerText;
        element.innerText = I18N.t('copied');
        setTimeout(() => {
            element.innerText = originalText;
        }, 1500);
    }
    document.body.removeChild(textarea);
}
function setupSwipeToDelete() {
    const rows = document.querySelectorAll('.tableDepartment');

    rows.forEach(row => {
        let startX = 0;
        let currentX = 0;
        let isDragging = false;

        const buttonWidth = 80;
        const maxShift = 140;

        // === КНОПКА УДАЛЕНИЯ ===
        let deleteBtn = document.createElement("div");
        deleteBtn.classList.add("delete-btn");
        deleteBtn.innerText = I18N.t('delete');
        deleteBtn.onclick = () => deleteRowInfo(row.id);
        row.appendChild(deleteBtn);

        // Убираем выделение
        row.style.userSelect = "none";
        row.style.position = "relative";
        row.style.transition = "transform 0.2s ease-out";

        // Вибро
        const vibrate = (ms = 20) => {
            if (navigator.vibrate) navigator.vibrate(ms);
        };

        // Плавное удаление без дрожания
        const swipeDelete = () => {
            row.style.transition = "transform 0.25s ease-out";
            row.style.transform = "translateX(-200%)";
            vibrate(30);

            setTimeout(() => deleteRowInfo(row.id), 180);
        };

        // === СВАЙП ===

        row.addEventListener("pointerdown", e => {
            startX = e.clientX;
            isDragging = true;
            row.style.transition = "none";
        });

        row.addEventListener("pointermove", e => {
            if (!isDragging) return;

            currentX = startX - e.clientX;
            if (currentX < 0) currentX = 0;
            if (currentX > maxShift) currentX = maxShift;

            row.style.transform = `translateX(-${currentX}px)`;
            deleteBtn.style.right = `-${buttonWidth - Math.min(buttonWidth, currentX)}px`;

            if (currentX >= buttonWidth && currentX < buttonWidth + 1) vibrate();
        });

        row.addEventListener("pointerup", () => {
            isDragging = false;
            row.style.transition = "transform 0.2s ease-out";

            if (currentX > maxShift * 0.75) {
                // Полное смахивание — удаляем
                swipeDelete();
                return;
            }

            if (currentX > buttonWidth) {
                // Показать кнопку
                row.style.transform = `translateX(-${buttonWidth}px)`;
                deleteBtn.style.right = "0";
            } else {
                // Вернуть назад
                row.style.transform = "translateX(0)";
                deleteBtn.style.right = `-${buttonWidth}px`;
            }

            currentX = 0;
        });

        row.addEventListener("pointerleave", () => {
            if (!isDragging) return;
            row.style.transition = "transform 0.2s ease-out";
            row.style.transform = "translateX(0px)";
            deleteBtn.style.right = `-${buttonWidth}px`;
            isDragging = false;
        });
    });
}
