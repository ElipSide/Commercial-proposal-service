var key = '', User_Info, check_info, tg, List_CP,data_CP, ID_provider, id_manager = '', UserName
var Price_KP
var ArrSelect = []
var Ids_ListSieve = []
var list_Product = []
var IndexList = []
var ListMachine = []
var List_Provider = []
var All_ListMachine, All_compressor, All_list_Product, All_IndexList,All_Service, All_Ids_ListSieve, All_warranty, All_delivery_terms, All_payment_method, All_parametrs, All_ListPhotoMachine, All_laboratory_equipment,All_extra_equipment, All_counterparty, All_group_names, All_attendance, All_elevator,All_pneumatic_feed
var result = {}, machine = [],TermDate, ID_USER,UserName,lastDay, CountList = [], keySieve=[], checkList = [], DopSieve = []

var ToglRead = true
pages = 'offer'
List_translate = {}
window.onload = async function() {
    await I18N.load(lang, 'common');


    tg = window.Telegram.WebApp;
    tg.disableVerticalSwipes()
    tg.expand(); //расширяем на все окно
    href = window.location.href
    tg.MainButton.hide() 
    // tg.BackButton.hide()
    ID_USER =  new URL(href).searchParams.get('tg_id')
    UserName = new URL(href).searchParams.get('username')
    Deal_id = new URL(href).searchParams.get('deal')!= null ? new URL(href).searchParams.get('deal') : 0
    new URL(href).searchParams.get('keyCP')!= null? ( key = new URL(href).searchParams.get('keyCP')) : writeNewCP('offer')
    document.getElementById('Number').innerText = `№${key}`

    getUserInfo()

    $("#mask-inn-organization").on('input', function(e){
        this.value = this.value.replace(/[^0-9\.]/g, '');
    });
    $("#mask-account").on('input', function(e){
        this.value = this.value.replace(/[^0-9\.]/g, '');
    });
    // GoodToast(I18N.t('loading'))
}

// НЕ ТРОГАТЬ
// Получение данных номенклатуры 
function getProd_list(){
    List = 'calc_sieve'
    $.ajax({
        url: `/off_bot/API/getListData/${lang}`,
        type: 'get',
        success: function (data) {
            All_list_Product = data['prod']
            All_IndexList = data['index']
            All_Ids_ListSieve = data['ids']
            All_ListMachine = data['machine']
            All_ListPhotoMachine = data['photoMachine'].sort((a, b) => a.id_row - b.id_row);
            All_Service = data['Service']
            All_compressor = data['kompressor']
            All_extra_equipment = Sorted_extra_equipment(data['extra_equipment'])
            All_group_names = data['group_names']
            All_attendance = data['attendance']
            All_elevator = data['Elevator']
            All_pneumatic_feed = data['Pneumatic_feed']

            All_laboratory_equipment = data['laboratory_equipment']

            

          new URL(href).searchParams.get('number_calk')!= null? ( addElevator_for_link()) : 0

          getConditions_list()
          },
          error: function (error) {
            Error_Message(`getListData error ${ID_USER}\n${error}`)
          }
    });
}

// удаление строки номенклатуры кп (ui)
function deleteRowInfo(id){
    var ID_M = document.getElementById(id).children[0].id
    id_el = ID_M.split('__')[2]
    type_el= ID_M.split('__')[1]
    delete data_CP['group_info'][type_el][id_el]
    if(type_el == 'elevator'){
        delete data_CP['additional_info']['id_json'][id_el]
    }
    document.getElementById(id).remove()
    UpdateCPlist(data_CP, List_CP, 'offer')
    СonditionsData()
    StartClone()
}
function calcPrice(basePrice, group, id, discountValue) {
    let price = basePrice;

    // индивидуальная скидка
    if (changed_sale_List[group]?.[id] !== undefined) {
        price *= (100 - changed_sale_List[group][id]) / 100;
    }

    // общая скидка
    if (
        changed_sale_List[group] === undefined ||
        changed_sale_List[group]?.[id] === undefined
    ) {
        if (discountValue !== 1) {
            price *= discountValue;
        }
    }

    return price;
}


const GROUPS_CONFIG = {
    Sieve: {
        source: () => All_Ids_ListSieve,
        key: 'id',
        name: el => `решето ${el.Type.toLowerCase()} ${el.Count.toFixed(1)}`,
        remainder: true
    },
    sep_machine: {
        source: () => All_ListMachine,
        key: 'id_row',
        name: el => el.name
    },
    photo_sorter: {
        source: () => All_ListPhotoMachine,
        key: 'id_row',
        name: el => `${el.name} ${el.configuration.replace(I18N.t('noConfiguration'), '')}`
    },
    Pneumatic_feed: {
        source: () => All_pneumatic_feed,
        key: 'id_row',
        name: el => el.name
    },
    elevator: {
        source: () => All_elevator,
        key: 'id_row',
        name: el => el.name
    },
    compressor: {
        source: () => All_compressor,
        key: 'id_row',
        name: el => el.name
    },
    extra_equipment: {
        source: () => All_extra_equipment,
        key: 'id_row',
        name: el => el.name
    },
    Service: {
        source: () => All_Service,
        key: 'id_row',
        name: el => el.name,
        priceFixed: true
    },
    attendance: {
        source: () => All_attendance,
        key: 'id_row',
        name: el => el.name,
        priceFixed: true
    },
    laboratory_equipment: {
            source: () => All_laboratory_equipment,
            key: 'id_row',
            name: el => el.name,
            priceFixed: true
    }
    
};

function buildListCheck(discountValue) {
    const result = [];

    for (const group in GROUPS_CONFIG) {
        const groupData = data_CP.group_info[group];
        if (!groupData) continue;

        const cfg = GROUPS_CONFIG[group];
        const source = cfg.source();

        for (const id of Object.keys(groupData)) {
            const el = source.find(f => f[cfg.key] == id);
            if (!el) continue;

            let price = changed_price_List[group]?.[id] ?? el.price;
            price = calcPrice(price, group, id, discountValue);

            result.push({
                name: cfg.name(el),
                count: groupData[id],
                price: cfg.priceFixed ? Number(price).toFixed(0) : price,
                sum: price * groupData[id],
                id: `deleteRow__${group}__${el[cfg.key]}`,
                id_erp: el.id_erp,
                remainder: cfg.remainder ? el.remainder : undefined
            });
        }
    }

    return result;
}

function StartClone() {

    if (data_CP.additional_info.nds !== undefined) {
        document.getElementById('nds').value = data_CP.additional_info.nds;
    }

    const TermDate = List_CP.creation_date;
    document.getElementById('Date').innerText = TermDate;
    document.getElementById('textTerm').innerText = `3 ${I18N.t('calendarDays')} ${I18N.t('startingFrom')} ${TermDate}`

    const discountValue =
        1 - document.getElementById('discount_input').value / 100;

    Price_KP = 0;
    ListCheck = buildListCheck(discountValue);

    // ===== ТВОЯ DOM-ЛОГИКА (НЕ ТРОГАЕМ) =====
    const Parent = document.getElementById('blockTable');
    for (let n = Parent.children.length - 1; n >= 3; n--) {
        Parent.children[n].remove();
    }

    const Children = Parent.children[1];

    for (let i = 0; i < ListCheck.length; i++) {
        const Clone = Children.cloneNode(true);
        Clone.style.display = 'flex';

        const index = Parent.children.length - 2;
        Clone.id = `tableDepartment_${index}`;

        Clone.children[0].innerText = index;
        Clone.children[0].id = `${ListCheck[i].id}__${index}`;
        Clone.children[1].id = `${ListCheck[i].id.replace('deleteRow', 'delete')}__${index}`;

        Clone.children[2].innerText = ListCheck[i].name;
        Clone.children[3].children[0].value = ListCheck[i].count;
        Clone.children[3].id = `${ListCheck[i].id.replace('deleteRow', 'ChangeCount')}__${index}`;
        Clone.children[3].children[1].innerText =
            Number(ListCheck[i].price).toLocaleString();

        if (ListCheck[i].remainder !== undefined) {
            Clone.children[4].children[1].id = `remainder_${ListCheck[i].id}__${index}`;
            Clone.children[4].children[1].innerText = `${I18N.t('remainder')}: ${ListCheck[i].remainder} ${I18N.t('pcs')}`

            if (ListCheck[i].remainder === 0) {
                Clone.style.backgroundColor = '#ff00004a';
                Clone.children[3].children[0].style.backgroundColor = 'transparent';
            }
        }

        if (
            (!ListCheck[i].id_erp || ListCheck[i].id_erp === "0") &&
            ListCheck[i].remainder !== 0
        ) {
            Clone.children[4].children[1].innerText = I18N.t('noERP')
            Clone.style.backgroundColor = 'rgb(252 255 10 / 50%)';
            Clone.children[3].children[0].style.backgroundColor = 'transparent';
        }

        const sum = Number(ListCheck[i].sum.toFixed(0));
        document.getElementById('nds').value === 'nds'
            ? Clone.children[4].children[0].innerText =
                (sum + sum * 0.2).toLocaleString()
            : Clone.children[4].children[0].innerText =
                sum.toLocaleString();

        Price_KP += sum;
        Parent.appendChild(Clone);
    }

    document.getElementById('Price_input').value =
        Price_KP.toLocaleString();

    data_CP.price = Price_KP;
    data_CP.sale = Number(document.getElementById('discount_input').value);

    ListCheck.length === 0
        ? (GetKP_button.style.display = 'none', infoBlock.style.display = 'none')
        : (GetKP_button.style.display = 'flex', infoBlock.style.display = 'flex');

    tg.MainButton.text !== I18N.t('back') && MainButton_func();

    setupSwipeToDelete();
    StartCloneInfo();
}


var  changed_price_List = {}
var changed_sale_List = {}

// открытие блока Изменения цены выбранной строки (ui)
function ChangeCount(id){
    var ID_M = id.split('__')[3]
    var ID_item  = id.split('__')[2]
    var type = id.split('__')[1]

    if (changed_price_List[type]) {
        change_price = changed_price_List[type][ID_item] ?? 
            Number(document.getElementById(`tableDepartment_${ID_M}`).children[3].children[1].innerText.replace(/\s/g, ''));
    } else {
        change_price = Number(document.getElementById(`tableDepartment_${ID_M}`).children[3].children[1].innerText.replace(/\s/g, ''));
    }


    document.getElementById('addButton_pos').style.display = 'none'
    document.getElementById('windowChange').style.display  = 'flex'
    document.getElementById('Blockprice_nds').style.display = 'none'
    document.getElementById('symbolNumber').style.display = 'none'
    User_Info['access_level']=='manager'
        ? document.getElementById('quantityAndPrice').innerText = I18N.t('quantityAndPrice')
        : document.getElementById('quantityAndPrice').innerText = I18N.t('quantity')
    document.getElementById('quantityAndPriceSelect').style.display = 'none'
    

    document.getElementById('windowChange').children[0].children[1].children[0].children[1].value = document.getElementById(`tableDepartment_${ID_M}`).children[3].children[0].value
    document.getElementById('windowChange').children[0].children[0].innerText = document.getElementById(`tableDepartment_${ID_M}`).children[2].innerText

    if(User_Info['access_level']=='manager'){  
        document.getElementById('windowChange').children[0].children[1].children[0].value = document.getElementById(`tableDepartment_${ID_M}`).children[3].children[0].value

        document.getElementById('windowChange').children[0].children[1].children[1].value = change_price
        if (changed_sale_List[type] && changed_sale_List[type][ID_item] !== undefined) {
            var value_sale = changed_sale_List[type][ID_item];
            var price_sale = ((100 - value_sale )/ 100) * change_price;
        } else {
            var value_sale = 0;
            var price_sale = change_price;
        }
        let windowChange = document.getElementById('windowChange');
        windowChange.children[1].children[0].children[1].children[0].value = value_sale;
        windowChange.children[1].children[1].children[1].children[0].innerText = price_sale.toLocaleString()
    }

    document.getElementById('SaveChange').id = id.replace('ChangeCount', 'SaveChange')
    var Parent = document.getElementById('blockTable')
    for (var n = Parent.children.length-1; n >= 3; n--){Parent.children[n].remove()}

    Blur_pointerEvent_on('topRow')
    Blur_pointerEvent_on('results')
    Blur_pointerEvent_on('infoBlock')
    tg.MainButton.hide()
    // tg.BackButton.hide()
}

// изменения цены и закрытие блока  (ui)
function SaveChange(id){
    Blur_pointerEvent_off('topRow')
    Blur_pointerEvent_off('results')
    Blur_pointerEvent_off('infoBlock')
    tg.MainButton.show()
    // tg.BackButton.hide()
    var type = id.split('__')[1]
    var Value = document.getElementById('changeBlock').value
    var ID_EL = id.split('__')[2]
    data_CP['group_info'][type][ID_EL] = Value
    if(User_Info['access_level']=='manager'){  

        changed_price_List[type] == undefined ? changed_price_List[type] = {} : 0
        changed_price_List[type][ID_EL] = Number(document.getElementById('windowChange').children[0].children[1].children[1].value.replace(/\s/g, ""))
        changed_sale_List[type] == undefined ? changed_sale_List[type] = {} : 0
        changed_sale_List[type][ID_EL] = Number(document.getElementById('discount_input_sale').value)
    }
    UpdateCPlist(data_CP, List_CP, 'offer')
    document.getElementById('addButton_pos').style.display = 'flex'
    document.getElementById('windowChange').style.display  = 'none'
    document.getElementById('windowChange').children[0].children[0].innerText = ''
    document.getElementById('windowChange').children[0].children[1].children[0].value = ''
    document.getElementById('Blockprice_nds').style.display = 'flex'
    document.getElementById('symbolNumber').style.display = 'flex'
    document.getElementById('quantityAndPrice').innerText  = 'Кол-во/Цена'
        document.getElementById('quantityAndPriceSelect').style.display = 'flex'

    document.getElementById(id).id = 'SaveChange'
    StartClone()
    if(User_Info['access_level']=='manager'){  
        document.getElementById('windowChange').children[0].children[1].children[1].value = ''
        SaveChangePrice()
        SaveChangeSale()
    }

}

var ArrMachine = {}, ListMAchine = {}
// отправка сообщение в ЛС пользователю при добавлении номенклатуры в кп (ui)
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
        'page':'KP'
    }
    SendMessage(data)
    Update_KP()
    UpdateCPlist(data_CP, List_CP, 'offer')
}

//  Создание блоков доп информации выбранной номенклатуры (ui)
function StartCloneInfo(){
    var Parent = document.getElementById('Parentdescription')
    for (var n = Parent.children.length-1; n >= 1; n--){Parent.children[n].remove()}
    var Children = Parent.children[0]
    ListType = ['sep_machine', 'compressor', 'photo_sorter', 'Pneumatic_feed', 'laboratory_equipment'] //'Service'
    for (var q in ListType){
        Type = ListType[q]
        for (var n in Object.keys(data_CP['group_info'][Type])){
            el_id = Object.keys(data_CP['group_info'][Type])[n]
            q==0?el = All_ListMachine.filter(function(f) { return f['id_row'] == el_id})[0]:0
            q==1?el = All_compressor.filter(function(f) { return f['id_row'] == el_id})[0]:0
            q==2?el = All_ListPhotoMachine.filter(function(f) { return f['id_row'] == el_id})[0]:0
            q==3? el = All_pneumatic_feed.filter(function(f) { return f['id_row'] == el_id})[0]:0
            q==4? el = All_laboratory_equipment.filter(function(f) { return f['id_row'] == el_id})[0]:0

            el_info = All_parametrs.filter(function(f) { return f['id'] == el_id && f['type_machine'] == TypeMAchine[Type]})
            if(el_info.length ==0){
                continue
            }
            var Clone = Children.cloneNode(true)
            Clone.style.display = 'flex'
            q==2 ?config = el['configuration'].replace('(Extra light)','').replace(I18N.t('noConfiguration'),'') : config = ''
            Clone.children[0].innerText = `${I18N.t('description')} ${el['name']} ${config}`
            console.log(el['photo'])
            if( el['photo']== '-'|| el['photo']== '' ){
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
                unit_of_measurement = (el_info[i]['unit_of_measurement'] !=null &&  el_info[i]['unit_of_measurement'] !='-') ? el_info[i]['unit_of_measurement'] : ''
                Clone_2.children[0].children[1].innerText = `${el_info[i]['value']} ${unit_of_measurement}`
                Parent_2.appendChild(Clone_2)
            }
            Parent.appendChild(Clone)
        }
    }
    ID_provider != undefined? СonditionsData():0
    // data_CP['pdf_send'] == false && Price_KP != 0? GetMessageKP('КП', '') :data_CP['pdf_send'] == true
}


function Termsofpayment(){
    List_terms = All_payment_method.filter(function(f) { return f['id_provider'] == ID_provider && f['payment_distribution'] == document.getElementById('TermspaymentSelect').value})[0]
    CountSell['Payment'] = List_terms["discount_value"], SummSell()
    document.getElementById('textPaymenTerms').innerText = List_terms["text"]
    List_CP['payment_method'] = List_terms["payment_distribution"]
    terms_payment = TermspaymentSelect.value
    UpdateCPlist(data_CP, List_CP, 'offer')
}
function DeliveryTime(){
    List_terms = All_delivery_terms.filter(function(f) { return f['id_provider'] == ID_provider})
    CountSell['Delivery'] = List_terms[document.getElementById('DeliveryTimeSelect').value]["discount_value"], SummSell()
    document.getElementById('textDeliveryTime').innerText = List_terms[document.getElementById('DeliveryTimeSelect').value]["text"]
    Delivery_time = DeliveryTimeSelect.value
    UpdateCPlist(data_CP, List_CP, 'offer')

}
function Warranty(){
    List_terms = All_warranty.filter(function(f) { return f['id_provider'] == ID_provider})
    CountSell['Warranty'] = List_terms[document.getElementById('WarrantySelect').value]["discount_value"], SummSell()
    document.getElementById('textWarranty').innerText = List_terms[document.getElementById('WarrantySelect').value]["text"]
    Guarantee = WarrantySelect.value
    UpdateCPlist(data_CP, List_CP, 'offer')

}
function SummSell(){
    // document.getElementById('discount_input').value =Number( Object.values(CountSell).reduce((a, b) => a + b, 0))
    rebildPrice(' ')
}

// ПЕРЕПИСАТЬ
function SendManagerInfo(){
    var date = new Date(check_info['lastmanager_invoice']);
    dateNext = date.setDate(date.getDate()+1);
    if (check_info['lastmanager_invoice'] == '' || new Date(check_info['lastmanager_invoice']) <= dateNext){
        if( id_manager == 0){
        }
        text =
        `${I18N.t('kpShort')} ${key} ${I18N.t('fromDate')} <strong>${List_CP['creation_date']}</strong>\n` +
        `${I18N.t('amountWithVat')} <strong>${Price_KP}</strong>\n` +
        `${I18N.t('validUntil')} <strong>${lastDay}</strong>`;
        data = {
            'tg_id': ID_USER,
            'UserName': UserName,
            'keyCP':key,
            'chatID':'-1002195710985',
            'text': text,
            'chat':'manager',
            'page' :'KP'
        }
        GoodToast(I18N.t('waitManager'))
        SendMessage(data)
        var date = new Date();
        date.setDate(date.getDate());
        invoice_time =date.toISOString().split('T')[0];
        check_info['lastmanager_invoice'] = invoice_time;
        Update_KP()
    }
    else{
        BadToast(I18N.t('requestAlreadySent'))
    }
}

function CloseManagerInfo() {
    var old_language = User_Info['language']
    if( old_language != document.getElementById('Language_code').value && User_Info['access_level']=='manager'){
        ID_provider==3?document.getElementById('companyManag').value = List_Provider.filter(function(f) {return f['id'] == 4})[0]['organization_shortname']:document.getElementById('companyManag').value = List_Provider.filter(function(f) {return f['id'] == 3})[0]['organization_shortname']
        List_CP['payment_method'] = ''
    }

    Telegram.WebApp.offEvent('mainButtonClicked', CloseManagerInfo);
    Telegram.WebApp.offEvent('mainButtonClicked', openUserInfo);
    Telegram.WebApp.offEvent('mainButtonClicked', openAD);

    if (document.getElementById('companyManag').value == '') {
        document.getElementById('companyManag').value = "ООО 'СИСОРТ'";
        User_Info['company'] = "ООО 'СИСОРТ'";
    }

    tg.MainButton.hide();


    ID_provider = List_Provider
        .filter(f => f.organization_shortname == User_Info['company'])[0]['id'];
    Update_KP();
    UpdateInfo_manager();
    MainButton_func();

    СonditionsData();


    ListChange.style.display = 'none';
    mainBlock.style.display = 'flex';
}



// открытие/закрытие блоков с данными при заполнии
function OpenBlock(id){
    if(User_Info['access_level']=='manager'){  
        CountCase = {'Name_CompanyBlock':2,'Name_CheckBlock':6,'Name_SignerBlock':8,'Name_buyerBlock':5,'Name_Comterms':3}
    }else{
        CountCase = {'Name_CompanyBlock':2,'Name_CheckBlock':4,'Name_SignerBlock':6,'Name_buyerBlock':3,}
    }
   if(document.getElementById(id.split('_')[1]).style.display == 'flex'){
       document.getElementById(id.split('_')[1]).style.display = 'none'

       document.getElementById(id.split('_')[1]).parentNode.children[CountCase[id]].children[1].style.backgroundImage = "url('/static/img/arrow_down.png')"
   }
   else{
       document.getElementById(id.split('_')[1]).style.display = 'flex'
       document.getElementById(id).style.backgroundColor = '#white'
       document.getElementById(id.split('_')[1]).parentNode.children[CountCase[id]].children[1].style.backgroundImage = "url('/static/img/arrow_up.png')"
   }
}

function viewsDopButtons(togl){
    if(ID_provider!=3){return}
    togl  == true  ? (download_Bitrix.style.display = 'flex' ): (download_Bitrix.style.display = 'none')
}

var check_list, typeBotton
function Search_prod_add(){
    CloneElMenu(check_list, typeBotton)
}




function clearChildrenFromSecond(parent) {
    for (var n = parent.children.length - 1; n >= 1; n--) {
        parent.children[n].remove()
    }
}

// блок для клонирования при создании меню
function CloneElMenu(check_list_product, typeBotton){
    if(document.getElementById('search_Search_teg').value !=''){
        check_list_product = check_list_product.filter(function(f) { return f['name'].toUpperCase().includes(document.getElementById('search_Search_teg').value.toUpperCase())})
    }
    else{
        check_list_product = check_list_product
    }

    let TegParent = document.getElementById('search_scrollBlock')
    clearChildrenFromSecond(TegParent)
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
    User_Info['access_level']!='manager'?addClassItem('Calk'):0
}

// блок ссылка для клонирования при создании блока калькуляторы
function CloneEllink(check_list_product){
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    clearChildrenFromSecond(TegParent)
    for (var i = 0; i < check_list_product.length; i++) {
        el_name = check_list_product[i].name
        el_count = check_list_product[i].id
        let TegClone = TegParent.children[0] .cloneNode(true)
        TegClone.style.display = 'flex'
        TegClone.children[0].textContent  = el_name
        TegClone.id = el_count
        TegParent.appendChild(TegClone);
        TegClone.addEventListener("click", function(){
            follow_link(this.id)
        }); 
    }
}
function scroll_Product_search(){
    typeBotton = 'Class'

    // выпадающий список со всеми товарами
    if(User_Info['access_level']=='manager'){  

        check_list = [
            { name: I18N.t('menuCalculators'), id: 'Calk' },
            { name: I18N.t('menuSieveMachines'), id: 'sep_machine' },
            { name: I18N.t('menuPhotoSorters'), id: 'photo_sorter' },
            { name: I18N.t('menuElevator'), id: 'elevator' },
            { name: I18N.t('menuPneumaticFeed'), id: 'Pneumatic_feed' },
            { name: I18N.t('menuCompressors'), id: 'compressor' },
            { name: I18N.t('menuExtraEquipment'), id: 'extra_equipment' },
            { name: I18N.t('laboratory_equipment'), id: 'laboratory_equipment' },
            { name: I18N.t('menuService'), id: 'Service' },
            { name: I18N.t('menuAttendance'), id: 'attendance' }

            
        ];

    }else{
        check_list = [
            { name: I18N.t('menuCalculators'), id: 'Calk' }
        ];

    }
    CloneElMenu(check_list, typeBotton)
}

var addType = ''
//  создание списков номенклатуры выбранной ранее группы
async function addClassItem(id_el){
    console.log(id_el)
    document.getElementById('search_Search_teg').value = ''
    if(document.getElementById('BlockBackInfo')!= null){
        User_Info['access_level']=='manager'?BlockBackInfo.style.display = 'flex':0
        BlockBackInfo.id = `BlockBackInfo__${1}`
    }
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    clearChildrenFromSecond(TegParent)
    var check_list_product
    addType = id_el
    var Togl_link = false
    typeBotton ='El'

    switch (id_el) {
        case 'Calk':
            Togl_link = true
            if(User_Info['access_level']=='manager'){  
                check_list_product = [
                    { name: I18N.t('productPhotoSorters'), id: 'Separator' },
                    // { name: I18N.t('productSieveMachines'), id: 'Sorting' },
                    { name: I18N.t('productElevator'), id: 'elevator' }
                ];

            }else{
                check_list_product = [
                    { name: I18N.t('productPhotoSorters'), id: 'Separator' },
                    { name: I18N.t('productElevator'), id: 'elevator' }
                ];
            }
            
            break
        case 'sep_machine':
            provider_List = All_ListMachine
            check_list_product = provider_List.map(item => ({
                name: item.name,
                id: `sep_machine__${item.id_row}`,
                id_provider: item.id_provider
            }));
            break
        case 'photo_sorter':
            el_list = [...new Set(All_ListPhotoMachine.map(item => item['name']))];
            check_list_product = el_list.map(item => ({
                name: item,
                id: `photo_sorter__${item}`,
                id_provider: All_ListPhotoMachine['id_provider']
            }));
            break
        case 'elevator':
            El_machine = []
            CreateCard(El_machine, 'elevator')

            break

        case 'Pneumatic_feed':
            el_list = [...new Set(All_pneumatic_feed.map(item => item['name']))];
            check_list_product = el_list.map(item => ({
                name: item,
                id: `Pneumatic_feed__${item}`,
                id_provider: All_pneumatic_feed['id_provider']
            }));
            break
            
        case 'Sieve':
            provider_List = All_Ids_ListSieve
            el_list = [...new Set(provider_List.map(item => item['Type']))];
            check_list_product = el_list.map(item => ({
                name: item,
                id: `Sieve__${item}`,
                id_provider: All_ListPhotoMachine['id_provider']
            }));
            break
        case 'compressor':
            provider_List = All_compressor
            check_list_product = provider_List.map(item => ({
                name: item.name,
                id: `compressor__${item.id_row}`,
                id_provider: item.id_provider
            }));
            break
        case 'extra_equipment':
            provider_List = All_extra_equipment
            check_list_product = provider_List.map(item => ({
                name: item.name,
                id: `extra_equipment__${item.id_row}`,
                id_provider: item.id_provider
            }));
            break
        case 'laboratory_equipment':
            provider_List = All_laboratory_equipment

            check_list_product = provider_List.map(item => ({
                name: item.name,
                id: `laboratory_equipment__${item.id_row}`,
                id_provider: item.id_provider
            }));
            dop_separ = All_ListPhotoMachine.filter(function(f) { return f['id_row'] == 153})[0]

         
            console.log(dop_separ)
            check_list_product.unshift({
                name: dop_separ.name,
                id: `photo_sorter__${dop_separ.name}`,
                id_provider: dop_separ.id_provider
            });
            
            dop_el = {
                "id_row": 0,
                "name": "Полный комплект оборудования",
                "name_print": "Полный комплект оборудования",
                "equipment_price": 0,
                "cost_price": 0,
                "price": 0,
                "markup": 0,
                "equipment": "",
                "id_provider": 3,
                "bitrix_id": "",
                "id_erp": "",
                "photo": ""
            }
            
            check_list_product.unshift({
                name: dop_el.name,
                id: `laboratory_equipment__${dop_el.id_row}`,
                id_provider: dop_el.id_provider
            });

            break

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
    if(id_el == 'elevator'){return}
    check_list = check_list_product
    
    Togl_link ? CloneEllink(check_list_product) :CloneElMenu(check_list_product, typeBotton)
}


// дополнительный шаг для выбора номенклатуры 
function addDopClassItem(id_el){
    document.getElementById('search_Search_teg').value = ''

    if( document.getElementById(`BlockBackInfo__${1}`)!= null){
        document.getElementById(`BlockBackInfo__${1}`).id = `BlockBackInfo__${1.5}__${id_el}`
    }
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    clearChildrenFromSecond(TegParent)
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
      document.getElementById('buttonNewCard').style.display = 'flex'

    id_el = id.split('__')[0]
    index_id = id.split('__')[1]
    document.getElementById(`BlockBackInfo__${1}`).id = `BlockBackInfo__${2}__${id_el}`
    let TegParent_count = document.getElementById('seleckBlock') //находим скрол  и чистим
    clearChildrenFromSecond(TegParent_count)
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    clearChildrenFromSecond(TegParent)
    switch (id_el) {
        case 'sep_machine':
            El_machine = All_ListMachine.filter(function(f) { return f['id_row'] == index_id})

            CreateCard(El_machine, 'sep_machine')
            break
        case 'photo_sorter':
            El_machine = All_ListPhotoMachine.filter(function(f) { return f['name'] == index_id})
            CreateCard(El_machine, 'photo_sorter')
            break

        case 'Pneumatic_feed':
            El_machine = All_pneumatic_feed.filter(function(f) { return f['name'] == index_id})
            CreateCard(El_machine, 'Pneumatic_feed')
            break
        case 'Sieve':
            El_Sieve = All_Ids_ListSieve.filter(function(f) { return f['Type'] == index_id})

            CreateCard(El_Sieve, 'Sieve')
            break
        case 'compressor':
            El_comp = All_compressor.filter(function(f) { return f['id_row'] == index_id})
            CreateCard(El_comp, 'compressor')
            break
        case 'extra_equipment':
            El_comp = All_extra_equipment.filter(function(f) { return f['id_row'] == index_id})
            CreateCard(El_comp, 'extra_equipment')
            break
        case 'laboratory_equipment':

            if(index_id ==0){
                const itemsToAdd = ["2", "3", "4", "5", "6", "7", "8"];

                data_CP.group_info.laboratory_equipment ??= {};

                itemsToAdd.forEach(key => {
                    data_CP.group_info.laboratory_equipment[key] =
                        (data_CP.group_info.laboratory_equipment[key] || 0) + 1;
                });
                const itemsToAdd_sort = ['153']
                itemsToAdd_sort.forEach(key => {
                    data_CP.group_info.photo_sorter[key] =
                        (data_CP.group_info.photo_sorter[key] || 0) + 1;
                });

               document.getElementById('BlockBackInfo__2__laboratory_equipment').id = 'BlockBackInfo'
                    CloseInfo()
                    UpdateCPlist(data_CP, List_CP, 'offer')
                    StartClone()
                    СonditionsData()
            }
            else{
                El_comp = All_laboratory_equipment.filter(function(f) { return f['id_row'] == index_id})
                CreateCard(El_comp, 'laboratory_equipment')
            }

            break

            
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
    clearChildrenFromSecond(TegParent_count)
    let TegParent = document.getElementById('search_scrollBlock') //находим скрол  и чистим
    clearChildrenFromSecond(TegParent)

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
    allprovider = [...new Set(index.map(item => Number(item['id_provider'])))];
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
        case 'sep_machine':
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = index[0].name_print
            document.getElementById('buttonNewCard').id = `buttonNewCard__sep_machine`
            break
        case 'photo_sorter':
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = index[0].name_print

            document.getElementById('Separ_configuration').style.display = 'flex'

            Parent = document.getElementById('Separ_configuration').children[1]
            for (var i = 0; i < index.length; i++) {
                let TegClone = Parent.children[0] .cloneNode(true)
                TegClone.value  = index[i]['configuration']
                TegClone.innerText = index[i]['configuration']
                TegClone.disabled = false
                Parent.appendChild(TegClone);
            }
            document.getElementById('buttonNewCard').id = `buttonNewCard__photo_sorter`
            break

        case 'Pneumatic_feed':
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = index[0].name //Заменить на     name_print    
            document.getElementById('buttonNewCard').id = `buttonNewCard__Pneumatic_feed`
            break
        case 'elevator':
            document.getElementById('Select_provider').style.display = 'none'
            document.getElementById('quantityPieces').style.display = 'none'
            document.getElementById('BlockChoiceMachine').style.display = 'none'
            document.getElementById('Select_elevator').style.display = 'flex'
            document.getElementById('buttonNewcheck').style.display = 'flex'
            document.getElementById('buttonNewcheckLink').style.display = 'flex'
            document.getElementById('buttonNewCard').id = `buttonNewCard__elevator`
            document.getElementById(`buttonNewCard__elevator`).style.display = 'none'

            break
        case 'Sieve':
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('SelectSieve').style.display = 'flex'
            document.getElementById('remainder').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = `${index[0]['Type']} решето`
            document.getElementById('remainder_Count').innerText = `${index[0]['remainder']} шт`
            document.getElementById('buttonNewCard').id = `buttonNewCard__Sieve`
            ChoiceProviderSieve()
            
            break
        case 'compressor':
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = index[0].name_print
            document.getElementById('buttonNewCard').id = `buttonNewCard__compressor`
            break
        case 'extra_equipment':
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = index[0].name
            document.getElementById('buttonNewCard').id = `buttonNewCard__extra_equipment`
            break
        case 'laboratory_equipment':
            document.getElementById('BlockChoiceMachine').style.display = 'flex'
            document.getElementById('ChoiceMachine').innerText = index[0].name
            document.getElementById('buttonNewCard').id = `buttonNewCard__laboratory_equipment`
            break

            
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

    // addType = ''

}


// добавление новой номенклатуры к общему списку и возврат всех параментов
function addNewCard(id){
    id_el = id.split('__')[1]
    countEl = Number(document.getElementById('quantityBlock').value)
    switch (id_el) {
        case 'sep_machine':
            document.getElementById('BlockBackInfo__2__sep_machine').id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__sep_machine').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_ListMachine.filter(function(f) { return f['name_print'] == name_print && f['id_provider']== Number(document.getElementById('seleckBlock_provider').value)})[0]['id_row']
            data_CP['group_info']['sep_machine'][id_machine] != undefined ? data_CP['group_info']['sep_machine'][id_machine]+= countEl: data_CP['group_info']['sep_machine'][id_machine] = countEl
            break
        case 'photo_sorter':
            document.getElementById('BlockBackInfo__2__photo_sorter').id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__photo_sorter').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_ListPhotoMachine.filter(function(f) { return f['name'] == name_print && f['id_provider']== Number(document.getElementById('seleckBlock_provider').value) && f['configuration']==document.getElementById('seleckBlock_lotoc').value})[0]['id_row']
            data_CP['group_info']['photo_sorter'][id_machine] != undefined ? data_CP['group_info']['photo_sorter'][id_machine]+= countEl: data_CP['group_info']['photo_sorter'][id_machine] = countEl

            break
        case 'Pneumatic_feed':
            document.getElementById('BlockBackInfo__2__Pneumatic_feed').id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__Pneumatic_feed').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_pneumatic_feed.filter(function(f) { return f['name'] == name_print && f['id_provider']== Number(document.getElementById('seleckBlock_provider').value) })[0]['id_row']
            data_CP['group_info']['Pneumatic_feed'][id_machine] != undefined ? data_CP['group_info']['Pneumatic_feed'][id_machine]+= countEl: data_CP['group_info']['Pneumatic_feed'][id_machine] = countEl

            break

        case 'elevator':
            document.getElementById('BlockBackInfo__1').id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__elevator').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_elevator.filter(function(f) { return f['name_print'] == name_print})[0]['id_row']
            data_CP['group_info']['elevator'][id_machine] != undefined ? data_CP['group_info']['elevator'][id_machine]+= countEl: data_CP['group_info']['elevator'][id_machine] = countEl
            document.getElementById('Select_elevator').children[1].value = ''

            break
        
        case 'Sieve':
            document.getElementById("BlockBackInfo__2__Sieve").id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__Sieve').id = `buttonNewCard`
            provider = document.getElementById('seleckBlock_provider').value
            count_sieve = Number(document.getElementById('seleckBlock').value)
            type = document.getElementById('ChoiceMachine').value.split(' ')[0]
            El_Sieve = All_Ids_ListSieve.filter(function(f) { return f['Count'] == count_sieve && f['id_provider']== provider && f['Type']== type })[0]['id']
            data_CP['group_info']['Sieve'][El_Sieve] != undefined ? data_CP['group_info']['Sieve'][El_Sieve]+= countEl: data_CP['group_info']['Sieve'][El_Sieve] = countEl
            break
        case 'compressor':
            document.getElementById('BlockBackInfo__2__compressor').id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__compressor').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_compressor.filter(function(f) { return f['name_print'] == name_print && f['id_provider']== Number(document.getElementById('seleckBlock_provider').value)})[0]['id_row']
            data_CP['group_info']['compressor'][id_machine] != undefined ? data_CP['group_info']['compressor'][id_machine]+= countEl: data_CP['group_info']['compressor'][id_machine] = countEl
            break
        case 'extra_equipment':
            document.getElementById('BlockBackInfo__2__extra_equipment').id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__extra_equipment').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_extra_equipment.filter(function(f) { return f['name'] == name_print && f['id_provider']== Number(document.getElementById('seleckBlock_provider').value)})[0]['id_row']
            data_CP['group_info']['extra_equipment'][id_machine] != undefined ? data_CP['group_info']['extra_equipment'][id_machine]+= countEl: data_CP['group_info']['extra_equipment'][id_machine] = countEl
            break
        case 'laboratory_equipment':
            document.getElementById('BlockBackInfo__2__laboratory_equipment').id = 'BlockBackInfo'
            document.getElementById('buttonNewCard__laboratory_equipment').id = `buttonNewCard`
            name_print = document.getElementById('ChoiceMachine').value
            id_machine = All_laboratory_equipment.filter(function(f) { return f['name'] == name_print && f['id_provider']== Number(document.getElementById('seleckBlock_provider').value)})[0]['id_row']
            data_CP['group_info']['laboratory_equipment'][id_machine] != undefined ? data_CP['group_info']['laboratory_equipment'][id_machine]+= countEl: data_CP['group_info']['laboratory_equipment'][id_machine] = countEl
            break


            
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
    togl_CloseInfo = true
    CloseInfo()
    openAD()
    UpdateCPlist(data_CP, List_CP, 'offer')
    StartClone()
    СonditionsData()
}


function ChoiceProviderSieve(){
    provider = Number(document.getElementById('seleckBlock_provider').value)
    type = document.getElementById('ChoiceMachine').value.split(' ')[0]
    index = All_Ids_ListSieve.filter(function(f) { return  f['id_provider']== provider && f['Type']== type })

    Parent = document.getElementById('SelectSieve').children[1]
    for (var n = Parent.children.length-1; n >= 1; n--) {
        Parent.children[n].remove()
    }
    for (var i = 0; i < index.length; i++) {
        if(provider !=index[i]['id_provider']){continue}
        let TegClone = Parent.children[0] .cloneNode(true)
        TegClone.value  = index[i]['Count']
        TegClone.innerText = index[i]['Count']
        TegClone.disabled = false
        Parent.appendChild(TegClone);
    }
    Choiceremainder_Count()
}
function Choiceremainder_Count(){
    provider = Number(document.getElementById('seleckBlock_provider').value)
    type = document.getElementById('ChoiceMachine').value.split(' ')[0]
    size = Number(document.getElementById('seleckBlock').value)
    index = All_Ids_ListSieve.filter(function(f) { return  f['id_provider']== provider && f['Type']== type  && f['Count'] == size})

    document.getElementById('remainder_Count').innerText = `${index[0]['remainder']} шт`
    index[0]['remainder'] == 0 ? document.getElementById('remainder').style.backgroundColor = '#ff00004a': document.getElementById('remainder').style.backgroundColor = 'white'
}


// кнопка-слайдер для переключение между договорм/счетом
function changeScoreContract(element) {
    if(document.getElementById('TextScoreContract').innerText == I18N.t('contract')){
        document.getElementById('TextScoreContract').innerText = I18N.t('invoice');
        download_Bitrix.style.display = 'none'
        download_Bitrix_ERP.style.display = 'none'
        Name_SignerBlock.style.display = 'none'
        SignerBlock.style.display = 'none';
        document.getElementById('drop-area').style.display = 'none'
        // fullListGet.style.display = 'none';
        download_agreement.style.display = 'none';
    } else {
        document.getElementById('TextScoreContract').innerText = I18N.t('contract');
        download_Bitrix.style.display = 'flex'
        download_Bitrix_ERP.style.display = 'flex'

        Name_SignerBlock.style.display = 'flex'
        SignerBlock.style.display = 'flex';
        document.getElementById('drop-area').style.display = 'none'
        // fullListGet.style.display = 'flex';
        download_agreement.style.display = 'flex';
    }
    checkbox_ScoreContract.checked = !checkbox_ScoreContract.checked
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
    document.getElementById('BlockAddRow').style.display = 'none'
    document.getElementById('Select_provider').style.display = 'none'
    document.getElementById('BlockChoiceMachine').style.display = 'none'
    document.getElementById('SelectSieve').style.display = 'none'
    document.getElementById('remainder').style.display = 'none'
    document.getElementById('Select_elevator').style.display = 'none'
    document.getElementById('Separ_configuration').style.display = 'none'
    document.getElementById('buttonNewcheck').style.display = 'none'
    document.getElementById('buttonNewcheckLink').style.display = 'none'

    switch (id_el) {
        case '1':
                addType = ''
                scroll_Product_search()
                document.getElementById(id).style.display = 'none'
                document.getElementById(id).id = 'BlockBackInfo'
                document.getElementById(`buttonNewCard__elevator`)!= undefined ?document.getElementById(`buttonNewCard__elevator`).id = 'buttonNewCard' :0

            break
        case '1.5':
            document.getElementById(id).id = `BlockBackInfo__${1}`
            addClassItem(index_id)
            break
        case '2':
            document.getElementById(id).id = `BlockBackInfo__${1}`
            document.getElementById(`buttonNewCard__${index_id}`).id = 'buttonNewCard'
            document.getElementById('search_filterBlock').style.display = 'flex'
            addClassItem(index_id)
            break
    }
}


function insert_dataEL(Arr_into){
    Choice_counter = ''
    document.getElementById('mask-inn-organization').value = Arr_into['inn']

    document.getElementById('mask-inn-organization').value = Arr_into['inn']
    document.getElementById('AdresUser').value = Arr_into['address']
    document.getElementById('UserData_inputNumber').value = Arr_into['phone_number']
    document.getElementById('emailUser').value = Arr_into['email']
    document.getElementById('mask-bik').value = Arr_into['bic']
    document.getElementById('mask-account').value = Arr_into['checking_account']
    document.getElementById('SelectProxy').value = Arr_into['basis']
    document.getElementById('textareaValid').value = Arr_into['number_proxy']
    document.getElementById('SignerBlock').children[0].children[0].value = Arr_into['patronymic'] 
    document.getElementById('SignerBlock').children[1].children[0].value = Arr_into['first_name'] 
    document.getElementById('SignerBlock').children[2].children[0].value = Arr_into['surname'] 
    check_info['acts_basis'] = Arr_into['basis']
    check_info['number_proxy'] = Arr_into['number_proxy']
    Comp_shortname.innerText = Arr_into['name']
    INNWrite()
    bicWrite()
    CheckSigner()
}


// создание json для отправки данных в битрикс 
function GetBitrix_json(){
    CheckCompany()
    Checkcheck()
    CheckSigner()

    // if(Name_CompanyBlock.style.backgroundColor  =='white' || Name_SignerBlock.style.backgroundColor =='white'){
    //     BadToast(I18N.t('fillCompanyInvoiceSigner'))
    //     return
    // }
    var price_listkp =[]
    var Parent = document.getElementById('blockTable')
    const toNum = (v) => {
        if (v == null) return NaN;
        const s = String(v)
            .replace(/\u00A0/g, ' ')      // NBSP
            .replace(/\s+/g, '')         // убрать пробелы-разделители тысяч
            .replace(/руб\.?|₽/gi, '')   // убрать валюту
            .replace(',', '.');          // на случай десятичных через запятую
        return Number(s);
    };

    for (let n = 3; n < Parent.children.length; n++) {
    const row = Parent.children[n];

    const id = row.children?.[1]?.id || "";
    const [_, type, name] = id.split('__');

    const sumText = row.children?.[4]?.children?.[0]?.innerText;
    const qtyVal  = row.children?.[3]?.children?.[0]?.value;

    const sum = toNum(sumText);
    const qty = toNum(qtyVal);

    const price = (Number.isFinite(sum) && Number.isFinite(qty) && qty !== 0)
        ? sum / qty
        : NaN;

    price_listkp.push({ name: Number(name), price, type });
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
            case 'Sieve':
              El_item = All_Ids_ListSieve.find(f => f['id'] === id_el);
              if(El_item== [] || El_item== undefined){continue}
              ListCheck_Agreement.push({
                'name': `решето ${El_item['Type'].toLowerCase()} ${(El_item['Count'].toFixed(1))}` ,
                'count' : count,
                'price': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'],
                'sum': price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count,
                'id': `deleteRow__${group}__${El_item['id_row']}`,
                "id_erp": El_item['id_erp']
              })
              Sum_ListCheck+= price_listkp.filter(function(f) { return f['name'] == id_el && f['type'] == group_key})[0]['price'] * count
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
                'id': `deleteRow__${group}__${El_item['id_row']}`,
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

  return data
}

function Getdeal_global(){

// WarningToast(I18N.t('creatingDeal'))
    const innValue = document.getElementById('mask-inn-organization').value.trim();
    const phoneValue = document.getElementById('UserData_inputNumber').value.trim();
    const emailValue = document.getElementById('emailUser').value.trim();

    const lengthINN = innValue.length;

    if (!(lengthINN === 10 || lengthINN === 12) && phoneValue === '' && emailValue === '') {
        BadToast(I18N.t('fillCompany'));
        return;
    }

    UserInfo_Block.style.filter = 'blur(2px)'
    UserInfo_Block.style.pointerEvents = 'none'

    SavePDF('Bitrix')
}

// создание сделки в битрикс
function Getdeal_Bitrix(){
    data = GetBitrix_json()
    data['CreateIn1сErp'] = false
    data['CategoryId'] = 1
    data['comment']=document.getElementById('textareaComment').value
    if(data['id_erp_manager'] ==''){
        BadToast(I18N.t('noERP'))
        return
    }
    data['Link'] = `https://t.me/Csort_official_bot?start=kp_${key}`
    Deal_id!=0? data['id_deal'] = Deal_id:data['id_deal'] =''

    PostAjax_bitrix(data)
}

// создание сделки в ERP

function Getdeal_ERP(){
    data = GetBitrix_json()
    data['CreateIn1сErp'] = true
    data['CategoryId'] = 1
    data['comment']= document.getElementById('textareaComment').value

    if(data['id_erp_manager'] ==''){
        BadToast(I18N.t('noERP'))
        return
    }
    
    data['Link'] = `https://t.me/Csort_official_bot?start=kp_${key}`
    Deal_id!=0? data['id_deal'] = Deal_id:data['id_deal'] =''

    PostAjax_bitrix(data)
}

// поотс запрос отправки данных для создания сделаки битрикс/erp
function PostAjax_bitrix(data){
    formData = JSON.stringify( data);
    $.ajax({
        type: 'post',
        url: `/off_bot/API/Get_Bitrix/${ID_USER}`,
        data: formData,
        processData: false,
        contentType: false,
        async: true,
        success: function(data){
            data_code = data['code']
            Deal_id = data['id_deal']
            download_Bitrix.children[0].innerText = 'Обновить сделку'
            UserInfo_Block.style.filter = 'none'
            UserInfo_Block.style.pointerEvents = 'auto'
            mainBlock.style.filter = 'none'
            mainBlock.style.pointerEvents = 'auto'
            if(data_code == 200 || data_code == 409 ){
                data_CP['additional_info']['link_deal'] = `https://csort24.bitrix24.ru/crm/deal/details/${Deal_id}/` 
                UpdateCPlist(data_CP, List_CP, 'offer')
                deal_bitrix_button.style.display = 'flex'
            }

            data_code == 200 ? GoodToast(I18N.t('dealCreated')) :0
            data_code == 405 ? BadToast(I18N.t('bitrixNoId1cChange')) : 0;
            data_code == 406 ? BadToast(I18N.t('erpManagerNotFound')) : 0;
            data_code == 407 ? BadToast(I18N.t('bitrixManagerNotFound')) : 0;
            data_code == 408 ? BadToast(I18N.t('requestTimeout')) : 0;
            data_code == 409 ? WarningToast(I18N.t('dealAlreadyExists')) : 0;
            data_code == 500 ? BadToast(I18N.t('internalError')) :0 


            el_row = All_counterparty.filter(function(f) { return (f['inn'])==document.getElementById('mask-inn-organization').value})[0]
            if(el_row==undefined){
                new_row = {
                    "name": check_info['organization_shortname'],
                    "orgn_ogrnip": check_info['ogrn'],
                    "inn": check_info['inn'],
                    "kpp": check_info['kpp'],
                    "address": check_info['address'],
                    "region": "Новгородская область",
                    "phone_number": check_info['phone_number'],
                    "email": check_info['email'],
                    "bank": check_info['bank_info'],
                    "correspondent_account": check_info['corporate_account'],
                    "bic": check_info['bic'],
                    "surname": check_info['second_name'],          
                    "first_name": check_info['first_name'],    
                    "patronymic": check_info['surname'],  
                    "basis": check_info['acts_basis'],
                    "basic_text": check_info['number_proxy'],
                    "checking_account": check_info['checking_account']
                }


                Write_counterpaty(new_row)

            }

            // data_CP["id_send_mess"] = data
        },
        error: function (error) {
            UserInfo_Block.style.filter = 'none'
            UserInfo_Block.style.pointerEvents = 'auto'
            BadToast(I18N.t('internalError'))
        Error_Message(`Get_Bitrix ${ID_USER}\n${error}`)
        } 
    }) 
}

function Write_counterpaty(data){
    formData = JSON.stringify( data);
    $.ajax({
        type: 'post',
        url: `/off_bot/API/write_counterparty`,
        data: formData,
        processData: false,
        contentType: false,
        async: true,
        success: function(data){
        },
        error: function (error) {
            Error_Message(`write_counterparty ${ID_USER}\n${error}`)
        } 
    }) 
}

// поотс запрос отправки данных для создания сделаки битрикс/erp
function PostAjax_bitrix_company(){
    ClearRecognize_data()
    $.ajax({
        type: 'post',
        url: `/off_bot/API/Get_Bitrix_company/${Deal_id}`,
        data: formData,
        processData: false,
        contentType: false,
        async: true,
        success: function(data){
            console.log(data)
            
            el_row = All_counterparty.filter(function(f) { return (f['inn'])==data['result']['inn']&& data['result']['inn']!=''})[0]
            console.log(el_row)

            if(el_row!=undefined){
                Choicecounter(`El_scrollBlock_${el_row['id_row']}`)
            }
            else{
                const map = {
                    inn: 'mask-inn-organization',
                    Address: 'AdresUser',
                    phone: 'UserData_inputNumber',
                    email: 'emailUser',
                    bik: 'mask-bik',
                    bankAccount: 'mask-account'
                };

                Object.entries(map).forEach(([key, elementId]) => {
                    if (data['result'][key]) {
                        const el = document.getElementById(elementId);
                        if (el) el.value = data['result'][key];
                    }
                });

                INNWrite()
                bicWrite()
                CheckSigner()

            }
        },
        error: function (error) {
            UserInfo_Block.style.filter = 'none'
            UserInfo_Block.style.pointerEvents = 'auto'
            BadToast(I18N.t('internalError'))
            Error_Message(`Get_Bitrix ${ID_USER}\n${error}`)
        } 
    }) 

}

async function addElevator_for_link(){
    var id_deal
    new URL(href).searchParams.get('number_calk')!= null? id_deal = new URL(href).searchParams.get('number_calk') : 0
    id_deal = id_deal.replace(',','.')
    
    $.ajax({
      type: 'get',
      url: `/off_bot/API/GetCalkElevator/${id_deal}`,
      processData: false,
      contentType: false,
      success: function(data){
        var el_height = 
        parseFloat(data['modelSize']['height'] || 0) +
        parseFloat(data['modelSize']['top_length'] || 0) +
        parseFloat(data['modelSize']['bottom_length'] || 0)+
        parseFloat(data['modelSize']['TransportLength'] || 0);
        data['modelName'].includes('CSZE')  ? el_height = Number(el_height.toFixed(0)) : 0
        data['modelName'].includes('CSCC')  ? el_height = Number(el_height.toFixed(1)) :     el_height    = el_height 
  
        
        El_elevator = All_elevator.filter(function(f) { return (f['model']).replace(' ', '').includes(data['modelName']) && f['height']==el_height})[0]
        if(El_elevator == undefined){
          BadToast(I18N.t('checkNumber'))
          return
        }
        changed_price_List['elevator'] == undefined ? changed_price_List['elevator'] = {} : 0
        changed_price_List['elevator'][El_elevator['id_row']] =  Number((Number(data['modelPrice'])*Number(data['NDS'])).toFixed(0))
        SaveChangePrice()
        data_CP['additional_info']['id_json'] == undefined ?  data_CP['additional_info']['id_json'] = {} :0
        data_CP['additional_info']['id_json'][El_elevator['id_row']] = id_deal
        name_print = El_elevator['name_print']
        id_machine = All_elevator.filter(function(f) { return f['name_print'] == name_print})[0]['id_row']
        data_CP['group_info']['elevator'][id_machine] != undefined ? data_CP['group_info']['elevator'][id_machine]+= 1: data_CP['group_info']['elevator'][id_machine] = 1
        UpdateCPlist(data_CP, List_CP, 'offer');
        

        redirect()
      },
      error: function (error) {
        BadToast(I18N.t('checkNumber'))
      }
    }) 
  
}

async function redirect(){
    await sleep(500)
    hrefPage =window.location.href.includes('127.0.0.1')== true ? `http://127.0.0.1:8000/off_bot/offer/home`: `https://csort-news.ru/off_bot/offer/home`
    window.location.href =` ${hrefPage}?keyCP=${key}&tg_id=${ID_USER}&username=${UserName}&deal=${Deal_id}`
}

