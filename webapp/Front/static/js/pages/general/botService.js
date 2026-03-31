var key = '', User_Info, check_info, tg, List_CP,data_CP, ID_provider = 3, id_manager = '', UserName
var Price_KP
var ArrSelect = []
var Ids_ListSieve = []
var list_Product = []
var IndexList = []
var ListMachine = []
var List_Provider = []
var  All_warranty, All_delivery_terms, All_payment_method, All_parametrs,  All_counterparty, All_Service, All_group_names, All_attendance

pages = 'Service'
window.onload = function() {
    tg = window.Telegram.WebApp;
    tg.disableVerticalSwipes()
    tg.expand(); //расширяем на все окно
    // tg.MainButton.text = "Договор/Счет"; //изменяем текст кнопки 
    // tg.MainButton.textColor = "#fff"; //изменяем цвет текста кнопки
    // tg.MainButton.color = "#e01818"; //изменяем цвет бэкграунда кнопки
    // Telegram.WebApp.onEvent('mainButtonClicked', openUserInfo)

    tg.MainButton.hide() 
    tg.BackButton.hide()
   
    href = window.location.href
    ID_USER =  new URL(href).searchParams.get('tg_id')
    UserName = new URL(href).searchParams.get('username')


    // new URL(href).searchParams.get('keyCP')!= null? ( key = new URL(href).searchParams.get('keyCP'), getKP_info()) : writeNewCP('Service')
    new URL(href).searchParams.get('keyCP')!= null? ( key = new URL(href).searchParams.get('keyCP')) : writeNewCP('Service')

    document.getElementById('Number').innerText = `№${key}`
    getUserInfo()
    $("#mask-inn-organization").on('input', function(e){
        this.value = this.value.replace(/[^0-9\.]/g, '');
    });
    $("#mask-account").on('input', function(e){
        this.value = this.value.replace(/[^0-9\.]/g, '');
    });
    
    // if(User_Info['access_level']=='manager'){  
    //     changeScoreContract()
    // }
}

function getProd_list(){
    List = 'calc_sieve'
    $.ajax({
        url: `/off_bot/API/getListData/${lang}`,
        type: 'get',
        success: function (data) {
            All_Service = data['Service']

            All_group_names = data['group_names']
            All_attendance = data['attendance']

            getConditions_list()
        },
        error: function (error) {
            Error_Message(`getListData error ${ID_USER}\n${error}`)
        }
    });
}

var result = {}, machine = [],TermDate, ID_USER,UserName,lastDay, CountList = [], keySieve=[], checkList = [], DopSieve = []
var ToglRead = true

function StartClone(){ 

    TermDate = List_CP['creation_date']
    document.getElementById('Date').innerText = TermDate
    document.getElementById('textTerm').innerText = `3 календарных дня начиная с ${TermDate}`
  
    Price_KP = 0
    ListCheck = []
    for (var n in Object.keys(data_CP['group_info']['Service'])){
        el_id = Object.keys(data_CP['group_info']['Service'])[n]
        el = All_Service.filter(function(f) { return f['id_row'] == el_id})[0]
        price_el = changed_price_List['Service']?.[el_id] ?? el['price'];

        ListCheck.push({
            'name': `${el['name']}`,
            'count' : data_CP['group_info']['Service'][el_id],
            'price': Number(price_el).toFixed(0),
            'sum': price_el * data_CP['group_info']['Service'][el_id],
            'id': `deleteRow__Service__${el['id_row']}`,
            "id_erp": el['id_erp']
        })
    }
    if(User_Info['access_level']=='manager'){  

        for (var n in Object.keys(data_CP['group_info']['attendance'])){
            el_id = Object.keys(data_CP['group_info']['attendance'])[n]
            el = All_attendance.filter(function(f) { return f['id_row'] == el_id})[0]
            price_el = changed_price_List['attendance']?.[el_id] ?? el['price'];

            
            if (changed_sale_List['attendance']?.[el_id] !== undefined) {
                price_el *= (100 - changed_sale_List['attendance'][el_id]) / 100;
            }
            // changed_sale_List['attendance']== undefined ?discount_value!= 1? price_el = price_el*discount_value:0 :0
            // if( changed_sale_List['attendance']!= undefined){
            //     if(changed_sale_List['attendance'][el_id]== undefined){
            //         discount_value!= 1? price_el = price_el*discount_value:0
            //     }
            // }

            ListCheck.push({
                'name': `${el['name']}`,
                'count' : data_CP['group_info']['attendance'][el_id],
                'price': Number(price_el).toFixed(0),
                'sum': price_el * data_CP['group_info']['attendance'][el_id],
                'id': `deleteRow__attendance__${el['id_row']}`,
                "id_erp": el['id_erp']
            })
        }
    }
    
    var Parent = document.getElementById('blockTable')
    for (var n = Parent.children.length-1; n >= 3; n--){Parent.children[n].remove()}

    var Children = Parent.children[1]

    for(var i = 0; i< ListCheck.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        index = Parent.children.length - 2
        Clone.id = `tableDepartment_${index}`
        Clone.children[0].innerText = index
        Clone.children[0].id = `${ListCheck[i]['id']}__${index}`
        Clone.children[1].id = `${ListCheck[i]['id'].replace('deleteRow', 'delete')}__${index}`

        Clone.children[2].innerText = ListCheck[i]['name']
        Clone.children[3].children[0].value = ListCheck[i]['count']
        Clone.children[3].id =  `${ListCheck[i]['id'].replace('deleteRow', 'ChangeCount')}__${index}`
        Clone.children[3].children[1].innerText = ListCheck[i]['price'].toLocaleString()
        price_el = ListCheck[i]['sum'].toFixed(0)
        Clone.children[4].innerText = price_el.toLocaleString()
        Price_KP+=Number(price_el)
        Parent.appendChild(Clone)
        Clone.children[0].addEventListener('mouseover', function(event) {
            // Изменяем цвет фона элемента при наведении курсора
            event.target.innerText = 'X';
        });
        Clone.children[0].addEventListener('mouseout', function(event) {
            // Изменяем цвет фона элемента при наведении курсора
            event.target.innerText = event.target.id.split('__')[3];
        });
         

    }
    document.getElementById('Price_input').value = (Price_KP).toLocaleString()
    data_CP['price'] = Price_KP

    ListCheck.length == 0 ?    infoBlock.style.display = 'none' :  infoBlock.style.display = 'flex'
    tg.MainButton.text != 'Назад' ? MainButton_func():0

    document.getElementById('Price_input').value = (Price_KP*(1-document.getElementById('discount_input').value/100)).toLocaleString()
}

// удаление строки номенклатуры кп
function deleteRowInfo(id){
    id_el = id.split('__')[2]
    type_el= id.split('__')[1]
    delete data_CP['group_info'][type_el][id_el]
    document.getElementById(id).parentNode.remove()
    UpdateCPlist(data_CP, List_CP, 'offer')
}
function ChangeCount(id){
    var ID_M = id.split('__')[3]
    console.log(  document.getElementById(`tableDepartment_${ID_M}`))

    document.getElementById('addButton_pos').style.display = 'none'
    document.getElementById('windowChange').style.display  = 'flex'
    document.getElementById('Blockprice_nds').style.display = 'none'
    document.getElementById('symbolNumber').style.display = 'none'
    document.getElementById('SumRow').innerText  = 'кол-во'
    document.getElementById('windowChange').children[0].children[0].innerText = document.getElementById(`tableDepartment_${ID_M}`).children[2].innerText
    document.getElementById('windowChange').children[0].children[1].children[0].value = document.getElementById(`tableDepartment_${ID_M}`).children[3].children[0].value
    document.getElementById('windowChange').children[0].children[1].children[1].value = document.getElementById(`tableDepartment_${ID_M}`).children[3].children[1].innerText
    document.getElementById('SaveChange').id = id.replace('ChangeCount', 'SaveChange')
    var Parent = document.getElementById('blockTable')
    for (var n = Parent.children.length-1; n >= 3; n--){Parent.children[n].remove()}
    Blur_pointerEvent_on('topRow')
    Blur_pointerEvent_on('results')
    Blur_pointerEvent_on('infoBlock')
    tg.MainButton.hide()
    tg.BackButton.hide()
}
var  changed_price_List = {}

function SaveChange(id){
    Blur_pointerEvent_off('topRow')
    Blur_pointerEvent_off('results')
    Blur_pointerEvent_off('infoBlock')
    tg.MainButton.show()
    tg.BackButton.hide()
    var type = id.split('__')[1]
    var Value = document.getElementById('changeBlock').value
    var ID_EL = id.split('__')[2]
    data_CP['group_info'][type][ID_EL] = Value

    changed_price_List[type] == undefined ? changed_price_List[type] = {} : 0
    changed_price_List[type][ID_EL] = Number(document.getElementById('windowChange').children[0].children[1].children[1].value.replace(/\s/g, ""))

    UpdateCPlist(data_CP, List_CP, 'offer')
    document.getElementById('addButton_pos').style.display = 'flex'
    document.getElementById('windowChange').style.display  = 'none'
    // document.getElementById('tableDepartment').style.display  = 'flex'
    document.getElementById('windowChange').children[0].children[0].innerText = ''
    document.getElementById('windowChange').children[0].children[1].children[0].value = ''
    document.getElementById('windowChange').children[0].children[1].children[1].value = ''

    document.getElementById('Blockprice_nds').style.display = 'flex'
    document.getElementById('symbolNumber').style.display = 'flex'

    document.getElementById('SumRow').innerText  = 'сумма'
    document.getElementById(id).id = 'SaveChange'
    StartClone()
    SaveChangePrice()
}

var ArrMachine = {}, ListMAchine = {}
// отправка сообщение в ЛС пользователю при добавлении номенклатуры в кп
function GetMessageKP(text, text_contr){
    text = `${text} ${key} от <strong>${List_CP['creation_date']}</strong>\nСумма руб. с ндс: <strong>${Price_KP}</strong>\n${text_contr}`
    data_CP['pdf_send']= true
    data = {
        'tg_id': ID_USER,
        'UserName': UserName,
        'keyCP':key,
        'chatID':ID_USER,
        'text': text,
        'chat':'client',
        'page':'Service'
    }
    SendMessage(data)
    Update_KP()
    UpdateCPlist(data_CP, List_CP, 'offer')
}
//  Создание блоков доп информации выбранной номенклатуры
function StartCloneInfo(){
    var Parent = document.getElementById('Parentdescription')
    for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
    var Children = Parent.children[0]
    ListType = ['Service']
    for (var q in ListType){
        Type = ListType[q]
        for (var n in Object.keys(data_CP['group_info'][Type])){
            el_id = Object.keys(data_CP['group_info'][Type])[n]
            q==0? el = All_Service.filter(function(f) { return f['id_row'] == el_id})[0]:0
            el_info = All_parametrs.filter(function(f) { return f['id'] == el_id && f['type_machine'] == [Type]})
            var Clone = Children.cloneNode(true)
            Clone.style.display = 'flex'
            q==2 ?config = el['configuration'] : config = ''
            Clone.children[0].innerText = `Описание ${el['name']} ${config}`
            if( el['photo']== null|| el['photo']== '-'){
                Clone.children[1].children[0].children[0].style.display = 'none'
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
    ID_provider != undefined? СonditionsData():0
    // data_CP['pdf_send'] == false && Price_KP != 0? GetMessageKP('КП', '') :data_CP['pdf_send'] == true
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

function OpenManagerInfo(){
    tg.MainButton.hide()
    ListChange.style.display = 'flex'
    mainBlock.style.display = 'none'
}
function CloseManagerInfo(){
    tg.MainButton.show() 
    Update_KP()
    ID_provider = List_Provider.filter(function(f) { return f['organization_shortname'] == User_Info['company']})[0]['id']
    UpdateInfo_manager()

    ListChange.style.display = 'none'
    mainBlock.style.display = 'flex'
}





// открытие/закрытие блоков с данными при заполнии
function OpenBlock(id){
     CountCase = {
        'Name_CompanyBlock':2,
        'Name_CheckBlock':4,
        'Name_SignerBlock':6,
        'Name_buyerBlock':3,
    }
    if(document.getElementById(id.split('_')[1]).style.display == 'flex'){
        document.getElementById(id.split('_')[1]).style.display = 'none'
        console.log(id)

        console.log(CountCase[id])
        document.getElementById(id.split('_')[1]).parentNode.children[CountCase[id]].children[1].style.backgroundImage = "url('/off_bot/static/img/arrow_down.png')"
    }
    else{
        document.getElementById(id.split('_')[1]).style.display = 'flex'
        document.getElementById(id).style.backgroundColor = '#white'
        document.getElementById(id.split('_')[1]).parentNode.children[CountCase[id]].children[1].style.backgroundImage = "url('/off_bot/static/img/arrow_up.png')"
    }
}

// ActsOnTheBasis = {
//     'Устав':'Устава',
//     'Свидетельство':'Свидетельства',
//     'Доверенность':'Доверенности'
// }





var check_list, typeBotton
function Search_prod_add(){
    console.log(check_list, typeBotton)
    CloneElMenu(check_list, typeBotton)
}

// блок для клонирования при создании меню
function CloneElMenu(check_list_product, typeBotton){
    console.log(check_list_product)
    if(document.getElementById('search_Search_teg').value !=''){
        check_list_product = check_list_product.filter(function(f) { return f['name'].toUpperCase().includes(document.getElementById('search_Search_teg').value.toUpperCase())})
    }
    else{
        check_list_product = check_list_product
    }

    let TegParent = document.getElementById('search_scrollBlock')
    for (var n = TegParent.children.length-1; n >= 1; n--) {
        TegParent.children[n].remove()
    }
    for (var i = 0; i < check_list_product.length; i++) {
        el_name = check_list_product[i].name
        el_count = check_list_product[i].id
        let TegClone = TegParent.children[0] .cloneNode(true)
        TegClone.style.display = 'flex'
        TegClone.children[0].textContent  = el_name
        TegClone.id = el_count
        TegParent.appendChild(TegClone);
        TegClone.addEventListener("click", function(){
            if(typeBotton=='PodClass'){addDopClassItem(this.id)}
            if(typeBotton=='Dop_El'){Dop_addItem(this.id)}

            if(typeBotton=='Class'){addClassItem(this.id)}
            if(typeBotton=='El'){addItem(this.id)}

        }); 
    }
}
function scroll_Product_search(){
    typeBotton = 'Class'
    console.log(User_Info['access_level'])
    // выпадающий список со всеми товарами
    if(User_Info['access_level']=='manager'){  
        check_list = [
            {'name':'Сервис',  'id':'Service'},
            {'name':'Услуги',  'id':'attendance'},
        ]
    }
    else{   
        check_list = [
            {'name':'Сервис',  'id':'Service'},
        ]
    }
    console.log(check_list)
    CloneElMenu(check_list, typeBotton)
}
var addType = ''

//  создание списков номенклатуры выбранной ранее группы
async function addClassItem(id_el){
    document.getElementById('search_Search_teg').value = ''
    if(document.getElementById('BlockBackInfo')!= null){
        BlockBackInfo.style.display = 'flex'
        BlockBackInfo.id = `BlockBackInfo__${1}`
    }
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    for (var n = TegParent.children.length-1; n >= 1; n--) {
        TegParent.children[n].remove()
    }
    var check_list_product
    addType = id_el
    typeBotton ='El'

    switch (id_el) {
        case 'Service':
            provider_List = All_group_names
            check_list_product = provider_List.map(item => ({
                name: item.name,
                id: `Service__${item.id}`,
                id_provider: 3
            }));
            typeBotton ='PodClass'
            break 
        case 'attendance':
            provider_List = All_attendance
            check_list_product = provider_List.map(item => ({
                name: item.name,
                id: `attendance__${item.id_row}`,
                id_provider: 3
            }));
            break
    }
    check_list = check_list_product

    CloneElMenu(check_list_product, typeBotton)
}
// дополнительный шаг для выбора номенклатуры 
function addDopClassItem(id_el){
    document.getElementById('search_Search_teg').value = ''

    if( document.getElementById(`BlockBackInfo__${1}`)!= null){
        document.getElementById(`BlockBackInfo__${1}`).id = `BlockBackInfo__${1.5}__${id_el}`
    }
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    for (var n = TegParent.children.length-1; n >= 1; n--) {
        TegParent.children[n].remove()
    }
    console.log(id_el.split('__')[1])
    provider_List = All_Service.filter(function(f) { return f['groups'] == Number(id_el.split('__')[1])})
    name_group=All_group_names.filter(function(f) { return f['id'] == Number(id_el.split('__')[1])})[0]['name']
    check_list_product = provider_List.map(item => ({
        name: item.name,
        id: `${name_group}__${item.id_row}`,
        id_provider: 3
    }));

    addType = id_el.split('__')[1]
    typeBotton ='Dop_El'
    check_list = check_list_product
    CloneElMenu(check_list_product, typeBotton)

}
// определение выбранной номенклатуры
function addItem(id){
    document.getElementById('search_Search_teg').value = ''

    id_el = id.split('__')[0]
    index_id = id.split('__')[1]
    document.getElementById(`BlockBackInfo__${1}`).id = `BlockBackInfo__${2}__${id_el}`
    let TegParent_count = document.getElementById('seleckBlock') //находим скрол  и чистим
    for (var n = TegParent_count.children.length-1; n >= 1; n--) {
        TegParent_count.children[n].remove()
    }
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    for (var n = TegParent.children.length-1; n >= 1; n--) {
        TegParent.children[n].remove()
    }
    switch (id_el) {
        case 'Service':
            El_serv = All_Service.filter(function(f) { return f['id_row'] == index_id})
            CreateCard(El_serv, 'Service')
            break   
        case 'attendance':
            El_comp = All_attendance.filter(function(f) { return f['id_row'] == index_id})
            CreateCard(El_comp, 'attendance')
            break
    }


}

function Dop_addItem(id){
    document.getElementById('search_Search_teg').value = ''

    id_el = id.split('__')[0]
    index_id = id.split('__')[1]
    El_machine = All_Service.filter(function(f) { return f['id_row'] == index_id})
    document.getElementById(`BlockBackInfo__${1.5}__Service__${El_machine[0]['groups']}`).id = `BlockBackInfo__2__Service`
    let TegParent_count = document.getElementById('seleckBlock') //находим скрол  и чистим
    for (var n = TegParent_count.children.length-1; n >= 1; n--) {
        TegParent_count.children[n].remove()
    }
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    for (var n = TegParent.children.length-1; n >= 1; n--) {
        TegParent.children[n].remove()
    }
    console.log(El_machine, id_el)

    CreateCard(El_machine, 'Service')
}

// создание блока выбранной номенклатуры
function CreateCard(index, id){
    id_el = id.split('__')[0]
    index_id = id.split('__')[1]
    document.getElementById('search_filterBlock').style.display = 'none'
    document.getElementById('BlockAddRow').style.display = 'flex'
    document.getElementById('Select_provider').style.display = 'flex'
    Parent = document.getElementById('seleckBlock_provider')
    for (var n = Parent.children.length-1; n >= 1; n--) {
        Parent.children[n].remove()
    }
    allprovider = [...new Set(index.map(item => item['id_provider']))];
    for (var i = 0; i < List_Provider.length; i++) {
        if(allprovider.includes(List_Provider[i].id)==false){continue}
        el_name = List_Provider[i].organization_shortname
        el_id = List_Provider[i].id
        let TegClone = Parent.children[0] .cloneNode(true)
        TegClone.value  = el_id
        TegClone.innerText = el_name
        TegClone.disabled = false
        Parent.appendChild(TegClone);
       if(ID_provider== el_id){
            document.getElementById('seleckBlock_provider').value = el_id
        }
    }
    Parent = document.getElementById('seleckBlock_lotoc')
    for (var n = Parent.children.length-1; n >= 1; n--) {
        Parent.children[n].remove()
    }
    switch (id_el) {
        case 'Service':
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = index[0].name
            document.getElementById('buttonNewCard').id = `buttonNewCard__Service`
            break     

        case 'attendance':
            
            document.getElementById('Select_provider').style.display = 'none'
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = index[0].name
            document.getElementById('buttonNewCard').id = `buttonNewCard__attendance`
            break   
    }


}



// добавление новой номенклатуры к общему списку и возврат всех параментов
function addNewCard(id){
    id_el = id.split('__')[1]
    countEl = Number(document.getElementById('quantityBlock').value)
    switch (id_el) {
        case 'Service':
            document.getElementById(`BlockBackInfo__2__Service`).id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__Service').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_Service.filter(function(f) { return f['name'] == name_print && f['id_provider']== Number(document.getElementById('seleckBlock_provider').value)})[0]['id_row']
            data_CP['group_info']['Service'][id_machine] != undefined ? data_CP['group_info']['Service'][id_machine]+= countEl: data_CP['group_info']['Service'][id_machine] = countEl
            break 
        case 'attendance':
            document.getElementById(`BlockBackInfo__2__attendance`).id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__attendance').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_attendance.filter(function(f) { return f['name'] == name_print})[0]['id_row']
            data_CP['group_info']['attendance'][id_machine] != undefined ? data_CP['group_info']['attendance'][id_machine]+= countEl: data_CP['group_info']['attendance'][id_machine] = countEl
            
    }
    CloseInfo()
    openAD()
    UpdateCPlist(data_CP, List_CP, 'offer')
    StartClone()
}

// кнопка-слайдер для переключение между договорм/счетом
function changeScoreContract(element) {
    if(document.getElementById('TextScoreContract').innerText == 'Договор') {
        document.getElementById('TextScoreContract').innerText = 'Счет';
        Name_SignerBlock.style.display = 'none'
        SignerBlock.style.display = 'none';
        document.getElementById('drop-area').style.display = 'none'
        // fullListGet.style.display = 'none';
        download_agreement.style.display = 'none';
    } else {
        document.getElementById('TextScoreContract').innerText = 'Договор';
        Name_SignerBlock.style.display = 'flex'
        SignerBlock.style.display = 'flex';
        document.getElementById('drop-area').style.display = 'none'
        // fullListGet.style.display = 'flex';
        download_agreement.style.display = 'flex';
    }
    checkbox_ScoreContract.checked = !checkbox_ScoreContract.checked
}
// сон для задежки 
function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
// изменение данных кп
async function activateChanges(){
    var Parent = document.getElementById('blockTable')
    toglChange = false

    for (var n = 2; n < Parent.children.length; n++) {
        if(Parent.children[n].children[0].style.display == 'flex'){
            Parent.children[n].children[0].style.display = 'none'
            Parent.children[n].children[1].style.display = 'flex'
            Parent.children[n].children[3].children[0].readOnly = false
        }
        else {
            Parent.children[n].children[0].style.display = 'flex'
            Parent.children[n].children[1].style.display = 'none'
            Parent.children[n].children[3].children[0].readOnly = true
            toglChange = true
            if( Parent.children[n].style.pointerEvents == 'none'){continue}
            text = Parent.children[n].children[2].innerText
            
        }
    }
    toglChange== false? (document.getElementById('imgChange').src = '/off_bot/static/img/done.png', document.getElementById('imgChangeCancel').style.display = 'none') :(document.getElementById('imgChange').src = '/off_bot/static/img/change.png', document.getElementById('imgChangeCancel').style.display = 'none')
    await sleep(50)
    if( toglChange== true){
        dubl_result.length = {}
        var Parent = document.getElementById('blockTable')
        for (var n = Parent.children.length-1; n >= 3; n--) {Parent.children[n].remove()}
        StartClone()
            UpdateCPlist(data_CP, List_CP, 'offer')

    }
    
}

function BackInfo(id){
    id_el = id.split('__')[1]
    index_id =id.split('__')[2] 
    switch (id_el) {
        case '1':
                addType = ''
                scroll_Product_search()
                document.getElementById(id).style.display = 'none'
                document.getElementById(id).id = 'BlockBackInfo'

            break
        case '1.5':
            document.getElementById(id).id = `BlockBackInfo__${1}`
            addClassItem(index_id)
            break
        case '2':
            document.getElementById(id).id = `BlockBackInfo__${1}`
            document.getElementById(`buttonNewCard__${index_id}`).id = 'buttonNewCard'
            document.getElementById('search_filterBlock').style.display = 'flex'
            document.getElementById('BlockAddRow').style.display = 'none'
            document.getElementById('Select_provider').style.display = 'none'
            document.getElementById('BlockChoiceMachine').style.display = 'none'
            document.getElementById('SelectSieve').style.display = 'none'
            addClassItem(index_id)
            break
    }
}




function insert_dataEL(Arr_into){
    Choice_counter = ''
    document.getElementById('mask-inn-organization').value = Arr_into['inn']
    document.getElementById('AdresUser').value = Arr_into['address']
    document.getElementById('UserData_inputNumber').value = Arr_into['phone_number']
    document.getElementById('emailUser').value = Arr_into['email']
    document.getElementById('mask-bik').value = Arr_into['bic']
    document.getElementById('mask-account').value = Arr_into['checking_account']
    document.getElementById('SelectProxy').value = Arr_into['basis']
    document.getElementById('textareaValid').value = Arr_into['number_proxy']
    check_info['acts_basis'] = Arr_into['basis']
    check_info['number_proxy'] = Arr_into['number_proxy']
    Comp_shortname.innerText = Arr_into['organization_shortname']
    INNWrite()
    bicWrite()
}


// отправка данных в битрикс 
function GetBitrix(){
    
    if(User_Info['id_erp'] == '' || User_Info['id_erp']==  null){
        BadToast('Заполните Id_erp в настройках профиля')
        return
    }

    CheckCompany()
    Checkcheck()
    if(Name_CheckBlock.style.backgroundColor =='white' || Name_CompanyBlock.style.backgroundColor  =='white'){
        BadToast('Заполните все поля Компания, Счет и Подписант')
        return
    }

    var price_listkp =[]
    var Parent = document.getElementById('blockTable')
    for (var n = 3; n < Parent.children.length; n++) {
        price_listkp.push({
          'name':Number(Parent.children[n].children[1].id.split('__')[2]),
          'price': Number(Parent.children[n].children[4].innerText)/Number(Parent.children[n].children[3].children[0].value),
          'type':Parent.children[n].children[1].id.split('__')[1]
        })
    }

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
        case 'attendance':
            El_item = All_attendance.filter(function(f) { return  f['id_row'] === id_el})[0]
            break;
        }
        if(El_item!= undefined){
          ListCheck_Agreement.push({
              'name': El_item['name'],
              'count' : count,
              'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
              'sum': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count,
              'id': `deleteRow__Service__${el['id_row']}`,
              "id_erp": El_item['id_erp']
          })
          Sum_ListCheck+=price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count
        }
      }
    }

    check_info['invoice_sent'] = true
    data = ReturnData(ID_provider, ListCheck_Agreement)
    data['id_provider'] = ID_provider
    data['NameFile'] = data['seller']['organization_shortname'].replace(/"/g, '');
    data['key'] = key
    data['sum'] =  Price_KP.toLocaleString()
    data['Chat_id'] =  ID_USER
    data['Id_manager'] =  ID_USER
    data['date'] =  List_CP['creation_date']
    data['CreateIn1сErp'] = true
    data['CategoryId'] = 21

    if(data['id_erp_manager'] ==''){
        BadToast("Нет ID ERP")
        return
    }
    formData = JSON.stringify( data);
    UserInfo_Block.style.filter = 'blur(2px)'
    UserInfo_Block.style.pointerEvents = 'none'
    WarningToast('Создаем сделку в Bitrix24')
    console.log(data)
    $.ajax({
        type: 'post',
        url: `/off_bot/API/Get_Bitrix/${ID_USER}`,
        data: formData,
        processData: false,
        contentType: false,
        async: true,
        success: function(data){

        console.log(data)
        data == 200 ? GoodToast('Сделка создана успешно') :0
        data == 405 ? BadToast('Изменение не было обнаружено id1c в Bitrix24') :0 
        data == 406 ? BadToast('Менеджер не был найден id1c в 1C: ERP') :0 
        data == 407 ? BadToast('Менеджер не был найден id1c в Bitrix24') :0 
        data == 408 ? BadToast("Request Timeout") :0 
        data == 409 ? WarningToast('Сделка уже существует') :0
        data == 500 ? BadToast('Internal Server Error') :0 
        UserInfo_Block.style.filter = 'none'
        UserInfo_Block.style.pointerEvents = 'auto'

        // data_CP["id_send_mess"] = data
        },
        error: function (error) {
        Error_Message(`Get_Bitrix ${ID_USER}\n${error}`)
        } 
    }) 
  
}