var key = '', User_Info, check_info, tg, List_CP,data_CP, ID_provider, id_manager = ''
var Price_KP
var ArrSelect = []
var Ids_ListSieve = []
var list_Product = []
var IndexList = []
var ListMachine = []
var List_Provider = []
var All_ListMachine, All_compressor, All_list_Product, All_IndexList,All_Service,  All_Ids_ListSieve, All_warranty, All_delivery_terms, All_payment_method, All_parametrs, All_ListPhotoMachine, All_extra_equipment,All_laboratory_equipment,  All_counterparty

var TypeMAchine = {
  'sep_machine': '1',
  'photo_sorter': '2',
  'Sieve': '3',
  'compressor': '4',
  'extra_equipment': '5',
  'service': '6',
  'elevator': '7',
  'Pneumatic_feed':'8'
}

window.onload = function() {
    tg = window.Telegram.WebApp;
    tg.disableVerticalSwipes()
    tg.expand(); //расширяем на все окно
    href = window.location.href
    ID_USER =  new URL(href).searchParams.get('tg_id')
       new URL(href).searchParams.get('keyCP')!= null? ( key = new URL(href).searchParams.get('keyCP'), getKP_info()) : writeNewCP('offer')
    document.getElementById('Number').innerText = `№${key}`
}


function getKP_info(){
    $.ajax({
        url: `getKPInfo/${key}`,
        type: 'get',
        success: function (data) {
          console.log(data)
          List_CP = data['List'][0]
          List_CP['creation_date'] = List_CP['creation_date'].split('T')[0]
          data_CP = data['createKP'][0]
          if(List_CP['manager_id_tg']== ''){  ID_provider = 3}
          data['changed_price_List'] == null  ? changed_price_List = {}: changed_price_List = data['changed_price_List'][0]['List']

          getProd_list()
        },
        error: function (error) {
            console.log('error', error);
        }
    });
}
function getProd_list(){
    List = 'calc_sieve'

    $.ajax({
        url: `getListData`,
        type: 'get',
        success: function (data) {
            All_list_Product = data['prod']
            All_IndexList = data['index']
            All_Ids_ListSieve = data['ids'] //.filter(function(f) { return f['id_erp'] != null})
            All_ListMachine = data['machine']
            All_ListPhotoMachine = data['photoMachine']
            All_Service = data['Service']
  
            All_compressor = data['kompressor']
            All_extra_equipment = data['extra_equipment']
            All_laboratory_equipment = data['laboratory_equipment']
          getProvider_list()
        
          },
        error: function (error) {
            console.log('error', error);
        }
    });
}


function getProvider_list(){

    $.ajax({
        url: `getProviderData`,
        type: 'get',
        success: function (data) {
          List_Provider = data['provider']
          getСonditions_list()
          },
          error: function (error) {
            // Error_Message(`getProviderData ${ID_USER}\n${error}`)
          }
    });
}

function getСonditions_list(){

    $.ajax({
        url: `getConditionsData`,
        type: 'get',
        success: function (data) {
          console.log(data)
          All_warranty=data['warranty']
          All_delivery_terms= data['delivery_terms']
          All_payment_method = data['payment_method']
          All_parametrs = data['dop_info']

          getUserInfo()

          },
        error: function (error) {
            console.log('error', error);
        }
    });
}
function getUserInfo(){
    console.log(key)
    $.ajax({
        url: `UserInfo_Key/${key}`,
        type: 'get',
        success: function (data) {
            User_Info = data['user'][0]
            if(User_Info['company'] !=''){
                ID_provider == undefined ? ID_provider = List_Provider.filter(function(f) { return f['organization_shortname'] == User_Info['company']})[0]['id'] :0
                UpdateInfo_manager()
            }
            ID_provider = 3
            StartClone()

        },
        error: function (error) {
            console.log('error', error);
        }
    });
}

function UpdateInfo_manager(){
    if(List_CP['manager_id_tg']!= ''){
        document.getElementById('company').innerText = User_Info['company']
        document.getElementById('mail').innerText= User_Info['mail']
        document.getElementById('FIO').innerText = `${User_Info['middle_name']} ${User_Info['name']}`
        document.getElementById('telephone').innerText= User_Info['phone_number']
        document.getElementById('BlockmanagerPhoto').poster =User_Info['photo']
        document.getElementById('introduction').innerText= User_Info['description']
        document.getElementById('post').innerText =User_Info['job_title']

    }
}
var result = {}, machine = [],TermDate, ID_USER,UserName,lastDay, CountList = [], keySieve=[], checkList = [], DopSieve = []
var  changed_price_List = {}

var ToglRead = true
const PDF_GROUPS_CONFIG = {
    Sieve: {
        source: function() { return All_Ids_ListSieve; },
        key: 'id',
        name: function(el) { return `решето ${el['Type'].toLowerCase()} ${el['Count'].toFixed(1)}`; }
    },
    sep_machine: {
        source: function() { return All_ListMachine; },
        key: 'id_row',
        name: function(el) { return el['name']; }
    },
    photo_sorter: {
        source: function() { return All_ListPhotoMachine; },
        key: 'id_row',
        name: function(el) { return `${el['name']} ${el['configuration']}`; }
    },
    compressor: {
        source: function() { return All_compressor; },
        key: 'id_row',
        name: function(el) { return el['name']; }
    },
    extra_equipment: {
        source: function() { return All_extra_equipment; },
        key: 'id_row',
        name: function(el) { return el['name']; }
    },
    laboratory_equipment: {
        source: function() { return All_laboratory_equipment; },
        key: 'id_row',
        name: function(el) { return el['name']; }
    },
    Service: {
        source: function() { return All_Service; },
        key: 'id_row',
        name: function(el) { return el['name']; },
        priceFixed: true
    }
};

function buildPdfListCheck() {
    const list = [];
    const groupInfo = data_CP['group_info'] || {};

    Object.keys(PDF_GROUPS_CONFIG).forEach(function(groupKey) {
        const cfg = PDF_GROUPS_CONFIG[groupKey];
        const groupData = groupInfo[groupKey] || {};
        const source = cfg.source();

        Object.keys(groupData).forEach(function(elId) {
            const el = source.find(function(item) { return item[cfg.key] == elId; });
            if (!el) {
                return;
            }

            const price = changed_price_List[groupKey]?.[elId] ?? el['price'];
            const count = groupData[elId];
            list.push({
                'name': cfg.name(el),
                'count': count,
                'price': cfg.priceFixed ? Number(price).toFixed(0) : price,
                'sum': price * count,
                'id': `deleteRow__${groupKey}__${el[cfg.key]}`,
                'id_erp': el['id_erp']
            });
        });
    });

    return list;
}

function StartClone(){

    TermDate = List_CP['creation_date']
    document.getElementById('Date').innerText = TermDate
    document.getElementById('textTerm').innerText = `3 календарных дня начиная с ${TermDate}`
  
    Price_KP = 0
    ListCheck = buildPdfListCheck()

    if(!Object.keys(data_CP['group_info']).includes('Sieve')){
        paymenTerms.style.display = 'none'
        deliveryTime.style.display = 'none'
        warranty.style.display = 'none'
    }

    var Parent = document.getElementById('blockTable')
    for (var n = Parent.children.length-1; n >= 3; n--){Parent.children[n].remove()}

    var Children = Parent.children[1]

    for(var i = 0; i< ListCheck.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        index = Parent.children.length - 1
        Clone.id = `tableDepartment_${index}`
        Clone.children[0].innerText = index
        Clone.children[0].id = `${ListCheck[i]['id']}__${index}`
        Clone.children[1].id = `${ListCheck[i]['id'].replace('deleteRow', 'delete')}__${index}`

        Clone.children[2].innerText = ListCheck[i]['name']
        Clone.children[3].children[0].value = ListCheck[i]['count']
        Clone.children[3].children[0].id =  `${ListCheck[i]['id'].replace('deleteRow', 'ChangeCount')}__${index}`
        Clone.children[3].children[1].innerText = Number(ListCheck[i]['price']).toLocaleString()
       

        price_el = ListCheck[i]['sum'].toFixed(0)
        document.getElementById('nds').value == 'nds' ?  Clone.children[4].innerText = (price_el + (0.2*price_el)).toLocaleString():  Clone.children[4].innerText = price_el.toLocaleString()
        Price_KP+=Number(price_el)
        
        Parent.appendChild(Clone)
        Clone.children[0].addEventListener('mouseover', function(event) {
            event.target.innerText = 'X';
        });
        Clone.children[0].addEventListener('mouseout', function(event) {
            event.target.innerText = event.target.id.split('__')[3];
        });
    }
    document.getElementById('Price_input').value = (Price_KP*(1-document.getElementById('discount_input').value/100)).toLocaleString()
    
    StartCloneInfo()
}

function rebildPrice(id){
    var Parent = document.getElementById('blockTable')
    AllPrice = 0
    for(var i = 1; i< Parent.children.length; i++){
        number = Number(Parent.children[i].children[4].innerText )
        console.log(number)
        id == 'nds' ?document.getElementById('nds').value == 'nds' ? Parent.children[i].children[4].innerText =(number +  (0.22*number)).toFixed(1) :  Parent.children[i].children[4].innerText =(number -( -1 * (number / (1 + 22/100) - number))).toFixed(1):0

        AllPrice += Number(Parent.children[i].children[4].innerText)
    }
    document.getElementById('Price_input').value = ( AllPrice*(1-document.getElementById('discount_input').value/100)).toFixed()
}
var ArrMachine = {}, ListMAchine = {}

// var TypeMAchine = {
//     'Sieve': '3',
//     'compressor': '4',
//     'photo_sorter': '2',
//     'sep_machine': '1',
//     'extra_equipment': '5'
// }
function StartCloneInfo(){

    if(Object.keys(data_CP['group_info']).includes('Sieve')){

        
        var Parent = document.getElementById('Parentdescription')
        for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
        var Children = Parent.children[0]

        ListType = ['sep_machine', 'compressor', 'photo_sorter']
        for (var q in ListType){
            Type = ListType[q]
            for (var n in Object.keys(data_CP['group_info'][Type])){
                el_id = Object.keys(data_CP['group_info'][Type])[n]
                
                q==0?el = All_ListMachine.filter(function(f) { return f['id_row'] == el_id})[0]:0
                q==1?el = All_compressor.filter(function(f) { return f['id_row'] == el_id})[0]:0
                q==2?el = All_ListPhotoMachine.filter(function(f) { return f['id_row'] == el_id})[0]:0

                el_info = All_parametrs.filter(function(f) { return f['id'] == el_id && f['type_machine'] == TypeMAchine[Type]})
                var Clone = Children.cloneNode(true)
                Clone.style.display = 'flex'
                q==2 ?config = el['configuration'] : config = ''
                Clone.children[0].innerText = `Описание ${el['name']} ${config}`
                console.log(el['photo'])
                if( el['photo']== '-' && q==2){
                    Clone.children[1].children[0].children[0].style.display = 'none'
                    // Clone.children[1].children[0].children[0].src =`/off_bot/static/img_machine/`
                }else{Clone.children[1].children[0].children[0].src =`/off_bot/static/img_machine/${el['photo'].replace('PNG','png').replace('jpg','png')}`}
                el['height']!= null ? Clone.children[1].children[1].children[0].children[1].children[0].innerText = el['height']:Clone.children[1].children[1].style.display = 'none'
                el['depth']!= null ? Clone.children[1].children[1].children[1].children[1].children[0].innerText = el['depth']:0
                el['width']!= null ? Clone.children[1].children[1].children[2].children[1].children[0].innerText = el['width']:0

                var Parent_2 =  Clone.children[1].children[3]
                var Child_2 = Parent_2.children[0]
                for(var i = 0; i< el_info.length; i++){
                        var Clone_2 = Child_2.cloneNode(true)
                        Clone_2.style.display = 'flex'
                        el_info[i]['parametr_name'].includes('__-')==true? el_info[i]['parametr_name'] = el_info[i]['parametr_name'].replace('__-','\n-'):0
                        el_info[i]['parametr_name'][0] === el_info[i]['parametr_name'][0].toUpperCase()? Clone_2.children[0].children[0].innerText = el_info[i]['parametr_name']: Clone_2.children[0].children[0].innerText = `-${el_info[i]['parametr_name']}`
                        if(el_info[i]['value']=='-'){continue}
                        Clone_2.children[0].children[1].innerText = `${el_info[i]['value']} ${el_info[i]['unit_of_measurement']}`
                        Parent_2.appendChild(Clone_2)
                }
                Parent.appendChild(Clone)

            }

        }
    }
    ID_provider != undefined? СonditionsData():0
    data_CP['pdf_send'] == false && Price_KP != 0? GetMessageKP('КП', '') :data_CP['pdf_send'] == true
    
}


function СonditionsData(){
    var List_terms = All_warranty.filter(function(f) { return f['id_provider'] == ID_provider})
    Parent = document.getElementById('WarrantySelect')
    for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
    var Children = Parent.children[0]
    for(var i = 0; i< List_terms.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        Clone.value = i
        document.getElementById('textWarranty').innerText = List_terms[i].text
        Clone.innerText = List_terms[i].warranty_period
        Parent.appendChild(Clone)
        i == 0? (document.getElementById('WarrantySelect').value = 0, CountSell['Warranty'] =List_terms[i].discount_value ) :0
    }
    Parent = document.getElementById('DeliveryTimeSelect')
    for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
    var Children = Parent.children[0]
    var List_terms = All_delivery_terms.filter(function(f) { return f['id_provider'] == ID_provider})
    for(var i = 0; i< List_terms.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        Clone.value = i
        document.getElementById('textDeliveryTime').innerText = List_terms[i].text
        Clone.innerText = List_terms[i].delivery_timeframe
        Parent.appendChild(Clone)
        i == 0? (document.getElementById('DeliveryTimeSelect').value = 0, CountSell['Delivery'] =List_terms[i].discount_value ) :0
    }
    Parent = document.getElementById('TermspaymentSelect')
    for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
    var Children = Parent.children[0]
    var List_terms = All_payment_method.filter(function(f) { return f['id_provider'] == ID_provider})
    for(var i = 0; i< List_terms.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        Clone.value = List_terms[i].payment_distribution
        // document.getElementById('textPaymenTerms').innerText = List_terms[i].text
        Clone.innerText = List_terms[i].payment_distribution
        Parent.appendChild(Clone)
        // i == 0? (document.getElementById('TermspaymentSelect').value = 0, CountSell['Payment'] =List_terms[i].discount_value ) :0
    }
    List_CP['payment_method']!=''?(document.getElementById('TermspaymentSelect').value = List_CP['payment_method']):document.getElementById('TermspaymentSelect').value  = '100% предоплата'
    Termsofpayment()
}


CountSell = {"Payment":'',    "Delivery":'',"Warranty":'',}
function Termsofpayment(){
    List_terms = All_payment_method.filter(function(f) { return f['id_provider'] == ID_provider && f['payment_distribution'] == document.getElementById('TermspaymentSelect').value})[0]
    CountSell['Payment'] = List_terms["discount_value"], SummSell()
    document.getElementById('textPaymenTerms').innerText = List_terms["text"]
    List_CP['payment_method'] = List_terms["payment_distribution"]

    terms_payment = TermspaymentSelect.value
}
function DeliveryTime(){
    List_terms = All_delivery_terms.filter(function(f) { return f['id_provider'] == ID_provider})
    CountSell['Delivery'] = List_terms[document.getElementById('DeliveryTimeSelect').value]["discount_value"], SummSell()
    document.getElementById('textDeliveryTime').innerText = List_terms[document.getElementById('DeliveryTimeSelect').value]["text"]
    Delivery_time = DeliveryTimeSelect.value
}
function Warranty(){
    List_terms = All_warranty.filter(function(f) { return f['id_provider'] == ID_provider})
    CountSell['Warranty'] = List_terms[document.getElementById('WarrantySelect').value]["discount_value"], SummSell()
    document.getElementById('textWarranty').innerText = List_terms[document.getElementById('WarrantySelect').value]["text"]
    Guarantee = WarrantySelect.value

}

function SummSell(){
    document.getElementById('discount_input').value =Number( Object.values(CountSell).reduce((a, b) => a + b, 0))
    rebildPrice(' ')
}

