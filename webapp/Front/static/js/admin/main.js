var filtered_sorted_rows = []
var modalActive = false;

var tg, ID_USER,UserName, key = '', id_provider, data_CP , List_CP
var togl_check = false
pages = 'Separator'
lang = 'ru'
var key_id
window.onload = function() {
    tg = window.Telegram.WebApp;
    tg.disableVerticalSwipes()
    tg.expand(); //расширяем на все окно
    // tg.MainButton.text = "Подобрать фотосепаратор"; //изменяем текст кнопки 
    // tg.MainButton.textColor = "#fff"; //изменяем цвет текста кнопки
    // tg.MainButton.color = "#e01818"; //изменяем цвет бэкграунда кнопки
    
    // Telegram.WebApp.onEvent('mainButtonClicked', GetInfoSepar)

    tg.MainButton.show() 
    href = window.location.href
    getList_name()
}
var Choice_table
var table
var param_sort = ''
var key_sort = ''
function openTable(id) {
    buttonCreate.style.display = 'flex';
    searchBar.style.display = 'flex';
    DeleteEl = []
    windowAllTables.style.display = 'none';
    windowAllProds.style.display = 'flex';
    var ID_M = id.split('_')[2]
    table = List_name_table.filter(function(f) {return f['id_row'] == ID_M})[0]
    $.ajax({
        url: `/off_bot/main_admin/get_choice_table/${table['name_table_db']}`,
        type: 'get',
        success: function (data) {
            // List_name_table = data['List_name_table']
            console.log('get_choice_table',data)
            tableProducts.innerText = `Таблица - ${table['name_table']}`

            Choice_table = data
            filtered_sorted_rows = Choice_table['List_table'];

            var key_id = Choice_table['Info_table'].includes('id')? 'id' :'id_row'
            param_sort = 'asc'
            key_sort =key_id
            filtered_sorted_rows = sortByKey(filtered_sorted_rows, key_sort, param_sort);

            Choice_table['List_table'] = sortByKey(Choice_table['List_table'], key_sort,param_sort)
            Clone_el_table(Choice_table, false)
        },
        error: function (error) {
                        console.log('get_choice_table',error)

            // Error_Message(`get_tables_name ${ID_USER}\n${error}`)
        }
    });
}

// универсальная сортировка(массив данных, ключ для сортировки, направление asc/desc)
function sortByKey(array, key, direction = 'asc', filterFn = null) {
  // Фильтрация массива, если предоставлена filterFn
  const filteredArray = filterFn ? array.filter(filterFn) : [...array];
  
  return filteredArray.sort((a, b) => {
    const getValue = (obj, k) => {
      // Обработка случаев, когда key - это функция
      if (typeof k === 'function') return k(obj);
      
      // Поддержка вложенных свойств через точку
      return k.split('.').reduce((o, i) => (o != null ? o[i] : null), obj);
    };
    
    const valueA = getValue(a, key);
    const valueB = getValue(b, key);
    const order = direction.toLowerCase() === 'desc' ? -1 : 1;

    // Обработка null/undefined
    if (valueA == null && valueB == null) return 0;
    if (valueA == null) return 1 * order;
    if (valueB == null) return -1 * order;

    // Сравнение массивов (по длине)
    if (Array.isArray(valueA) && Array.isArray(valueB)) {
      return (valueA.length - valueB.length) * order;
    }

    // Сравнение объектов (по количеству ключей)
    if (typeof valueA === 'object' && valueA !== null && 
        typeof valueB === 'object' && valueB !== null &&
        !(valueA instanceof Date) && !(valueB instanceof Date)) {
      const keysA = Object.keys(valueA);
      const keysB = Object.keys(valueB);
      return (keysA.length - keysB.length) * order;
    }

    // Сравнение дат
    if (valueA instanceof Date && valueB instanceof Date) {
      return (valueA - valueB) * order;
    }

    // Сравнение строк (с учетом чисел внутри строк)
    if (typeof valueA === 'string' && typeof valueB === 'string') {
      const numA = parseFloat(valueA);
      const numB = parseFloat(valueB);
      if (!isNaN(numA) && !isNaN(numB)) {
        return (numA - numB) * order;
      }
      return valueA.localeCompare(valueB) * order;
    }

    // Сравнение чисел
    if (typeof valueA === 'number' && typeof valueB === 'number') {
      return (valueA - valueB) * order;
    }

    // Сравнение разных типов (число vs строка)
    if (typeof valueA !== typeof valueB) {
      const numA = parseFloat(valueA);
      const numB = parseFloat(valueB);
      if (!isNaN(numA) && !isNaN(numB)) {
        return (numA - numB) * order;
      }
    }

    return 0;
  });
}

function objectToString(obj) {
    return JSON.stringify(obj);
}

// Функция для превращения строки в словарь
function stringToObject(str) {
    return JSON.parse(str);
}

function openWindowCreate(){
    document.getElementById('listInfoCreate').style.display = 'flex'
    document.getElementById('mainPage').style.filter = 'blur(2px)'
    document.getElementById('mainPage').style.pointerEvents = 'none'
}

function closeWindowCreate(){
    document.getElementById('listInfoCreate').style.display = 'none'
    document.getElementById('mainPage').style.filter = 'none'
    document.getElementById('mainPage').style.pointerEvents = 'auto'
}

function openDopSettings(){
    dopWindowSettings.style.display = 'flex';
}

function openDopSetPhoto(){
    dopWindSetPhoto.style.display = 'flex';
}

function gearWheelOpen(){
    document.getElementById('dopCategoriSet').style.display = 'flex'
    document.getElementById('mainPage').style.filter = 'blur(2px)'
    document.getElementById('mainPage').style.pointerEvents = 'none'
}

function gearWheelClose(){
    document.getElementById('dopCategoriSet').style.display = 'none'
    document.getElementById('mainPage').style.filter = 'none'
    document.getElementById('mainPage').style.pointerEvents = 'auto'
}

function closeCategSet(){
    document.getElementById('dopCategoriSet').style.display = 'none'
    document.getElementById('mainPage').style.filter = 'none'
    document.getElementById('mainPage').style.pointerEvents = 'auto'
}
var el_row
function openWindowInfo(id_row, id_row_name ){

    el_row = Choice_table['List_table'].filter(function(f) {return f[id_row_name]== id_row})[0]

    if(Object.keys(el_row).includes('name_console.log')){
        hardwareHeader.innerText = el_row['name_console.log']
    }
    else{
        hardwareHeader.innerText = table['name_table']

    }
    document.getElementById('blockInfoEquip').style.display = 'flex'
    document.getElementById('mainPage').style.filter = 'blur(2px)'
    document.getElementById('mainPage').style.pointerEvents = 'none'
    
    document.getElementById('WindowInfo_1').style.display = 'none'
    document.getElementById('WindowInfo_2').style.display = 'none'
    framePhotoEquip.style.filter = 'none'
    framePhotoEquip.style.pointerEvents = 'auto'

    if(!Choice_table['Info_table'].includes('photo') ){
        framePhotoEquip.style.filter = 'blur(2px)'
        framePhotoEquip.style.pointerEvents = 'none'
    }
    // generalInfoTwo
    var id_block = table['access_level'] == '1' ? 'generalInfo' : 'generalInfoTwo'
    table['access_level'] == '1'? document.getElementById('WindowInfo_1').style.display = 'flex':     document.getElementById('WindowInfo_2').style.display = 'flex'

    var Parent = document.getElementById(id_block)
    ClearBlock(Parent, 1)
    // !togl_filter? choice_colomn = []:0
    var Children = Parent.children[0]
    name_colomn = Object.keys(el_row)
    for(var n = 0; n< name_colomn.length; n++){
        let Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        // Clone.id = `tableNames_${n}`
        Clone.children[0].innerText = column_translations[name_colomn[n]]
      
        if(Array.isArray(el_row[name_colomn[n]])==false && typeof(el_row[name_colomn[n]])!='string'&& typeof(el_row[name_colomn[n]])!='number'&& typeof(el_row[name_colomn[n]])!='boolean' ){
            Clone.children[1].remove()
            let block = document.createElement('textarea')
            block.style.width =  '100%'
            block.style.height =  '80px'
            block.style.border = 'none'
            block.style.outline = 'none'

            block.setAttribute('readonly', 'true')
            block.value = objectToString(el_row[name_colomn[n]])
            Clone.appendChild(block)
        }else{
            Clone.children[1].value = el_row[name_colomn[n]]
            Clone.children[1].value ==''? Clone.children[1].placeholder = `Введите ${name_colomn[n]}` : 0
            if(name_colomn[n]=='id_provider' && el_row[name_colomn[n]] == 0){
                Clone.children[1].value = 3
            }
        }

        Clone.children[1].id = name_colomn[n]

       
        Parent.appendChild(Clone)
    }

    framePhotoEquip.children[0].style.display = 'flex'
    PhotoEquip.style.display = 'none'
    PhotoEquip.src = ''
    if(name_colomn.includes('photo') && el_row['photo']!=''){
    
        framePhotoEquip.children[0].style.display = 'none'
        PhotoEquip.style.display = 'flex'
        PhotoEquip.src = `/off_bot/static/img_machine/${el_row['photo']}`
    }
    // if(name_colomn.includes('price')){
    //     priceEquip.style.display = 'flex'
    //     priceEquip.innerText = el_row['price']
    // }

    // if(name_colomn.includes('name')){
    //     modelEquip.style.display = 'flex'
    //     modelEquip.innerText = el_row['name']
    // }
    
    renderAdditionalCharacteristics(el_row, id_row_name);

    setTimeout(() => modalActive = true, 80);

}

    // if(Object.keys(TypeMAchine).includes(table['name_table_db'])){
        
    //     var Parent = document.getElementById('characteristicInfo')
    //     ClearBlock(Parent, 1)
    //     // !togl_filter? choice_colomn = []:0
    //     var Children = Parent.children[0]
        
    //     dop_row = additional_parameters.filter(function(f) {return f['type_machine']== TypeMAchine[table['name_table_db']] && f['id']== el_row[id_row_name] && f['language']== el_row['language']})
    //     if(dop_row.length ==0){


    //     }

    //     for(var n = 0; n< dop_row.length; n++){
    //         let Clone = Children.cloneNode(true)
    //         Clone.style.display = 'flex'
    //         Clone.id = `idsAdditinfo_${dop_row[n]['id_row']}`
    //         Clone.children[1].id = `deleteidsAdditinfo_${dop_row[n]['id_row']}`

    //         Clone.children[0].children[0].innerText = `${dop_row[n]['parameter_name']}, ${dop_row[n]['unit_of_measurement']}`
    //         Clone.children[0].children[1].value = `${dop_row[n]['value']}`
           
    //         Parent.appendChild(Clone)
    //     }
    // }


    // setTimeout(() => modalActive = true, 80);

function renderAdditionalCharacteristics(el_row, id_row_name) {
    console.log('renderAdditionalCharacteristics', el_row, id_row_name)
    if (!Object.keys(TypeMAchine).includes(table['name_table_db'])) {
        return;
    }

    let Parent = document.getElementById('characteristicInfo');
    ClearBlock(Parent, 1);

    let Children = Parent.children[0];

    dop_row = additional_parameters.filter(function(f) {return f['type_machine']== TypeMAchine[table['name_table_db']] && f['id']== el_row[id_row_name]})

    console.log(dop_row)
    if (dop_row.length === 0) {
        return;
    }

    for (let n = 0; n < dop_row.length; n++) {
        let Clone = Children.cloneNode(true);
        Clone.style.display = 'flex';
        Clone.id = `idsAdditinfo_${dop_row[n]['id_row']}`;
        Clone.children[1].id = `deleteidsAdditinfo_${dop_row[n]['id_row']}`;

        Clone.children[0].children[0].innerText =
            `${dop_row[n]['parameter_name']}, ${dop_row[n]['unit_of_measurement']}`;

        Clone.children[0].children[1].value = `${dop_row[n]['value']}`;

        Parent.appendChild(Clone);
    }
}


function closeCrossBlockInfo(){

    var Block_id = WindowInfo_2.style.display=='flex' ? '2': '1'
    console.log(Block_id)
    document.getElementById(`changeInfo_${Block_id}`).style.display != 'none' ? 0: Save_change_el_info(`savechangeInfo_${Block_id}`)

    document.getElementById('blockInfoEquip').style.display = 'none'
    document.getElementById('mainPage').style.filter = 'none'
    document.getElementById('mainPage').style.pointerEvents = 'auto'
    modalActive = false; // <--- добавили
    Searcitem('')

}

// Закрытие окна при клике вне него
document.addEventListener('click', function (event) {

    if (!modalActive) return; // окно ещё не полностью открыто

    const modal = document.getElementById('blockInfoEquip');
    const windowBox = document.querySelector('.windowInfoEquip');

    // окно сейчас закрыто — ничего не делаем
    if (modal.style.display === 'none') return;

    // если клик внутри окна — не закрываем
    if (windowBox.contains(event.target)) return;

    // если клик по крестику — там уже есть onclick
    if (event.target.closest('#crossBlockInfoEq')) return;

    // закрываем
    closeCrossBlockInfo();
});


function saveApply(){
    Clone_el_table(Choice_table, true)
    gearWheelClose()
}
var List_name_table, additional_parameters
var TypeMAchine = {
    'separat_table': '1',
    'photo_separators': '2',
    'sieve_table': '3',
    'compressors': '4',
    'extra_equipment': '5',
    'service': '6',
    'elevator': '7',
    'Pneumatic_feed':'8',
    'laboratory_equipment':'9'

}
// Сортировка от меньшего к большему по access_level
function sortByAccessLevel(arr) {
    return arr.sort((a, b) => a.access_level - b.access_level);
}
column_translations = []
// Получение листа названий таблиц
function getList_name(){

    $.ajax({
        url: `/off_bot/main_admin/get_tables_name`,
        type: 'get',
        success: function (data) {
            List_name_table =sortByAccessLevel(data['List_name_table'])
            additional_parameters  = data['additional_parameters']
            column_translations = data['column_translations']
            Startmain_table()
        },
        error: function (error) {
            // Error_Message(`get_tables_name ${ID_USER}\n${error}`)
        }
    });
}

function Startmain_table(){
    var Parent = document.getElementById('blockProdStorageBox')
    ClearBlock(Parent, 1)
    var Children = Parent.children[0]
    allPages.innerText = `Дотупно таблиц к редактированию: ${List_name_table.length}`
    for(var i = 0; i< List_name_table.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        // Clone.style = 'display: flex; flex-direction: column; width: 100%; justify-content: center;  align-items: flex-start; height: 40px;'
        Clone.id = `blockProdStorageBox_children_${List_name_table[i]['id_row']}`
        Clone.children[0].innerText = List_name_table[i]['name_table']
        // document.getElementById('textPaymenTerms').innerText = List_terms[i].text
        // Clone.innerText = List_terms[i].payment_distribution
        Parent.appendChild(Clone)
    }

}

var maxInpage = document.getElementById('Select_maxRows').value
var Page_main = 1
var choice_colomn = []
function Clone_el_table(el_table, togl_filter){
    ClearTableinfo()
    var Parent = document.getElementById('filter_block')
    // ClearBlock(Parent, 1)
    var Children = Parent.children[0]
    var Clone = Children.cloneNode(true)
    Clone.style.display = 'flex'
    Clone.id = `filterNames_${table['name_table_db']}`

    Clone.children[0].innerText = `Раздел: ${table['name_table']}`
    Parent.appendChild(Clone)


    
    name_colomn = el_table['Info_table']
    // name_colomn = normalizeColumns(el_table['Info_table']);

    // берём только текущий набор (поиск/фильтр/сортировка)
    rows_table = filtered_sorted_rows;

    infoblockNumderPage.innerText = `Всего строк: ${rows_table.length}`


    // клонирование элементов в настройках таблицы 
    var Parent = document.getElementById('selectionBlock')
    // ClearBlock(Parent, 1)

    !togl_filter? choice_colomn = []:0

    var Children = Parent.children[0]

    for(var n = 0; n< name_colomn.length; n++){
        
        let Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        if(!togl_filter){
            choice_colomn.push(name_colomn[n])
        }
        choice_colomn.includes(name_colomn[n])? Clone.children[0].checked = true :0

        Clone.id = `tableNames_${n}`
        Clone.children[1].id = name_colomn[n]

        Clone.children[1].innerText = column_translations[name_colomn[n]]
        Parent.appendChild(Clone)
    }

    // клонирование названий колонок  

    var Parent = document.getElementById('allProds')
    // ClearBlock(Parent, 2)
    var Children = Parent.children[1]
    togl_rows = true
    for(var n = 0; n< name_colomn.length; n++){
      
        if(choice_colomn.includes(name_colomn[n])==false){continue}
        let Clone = Children.cloneNode(true)


        if(name_colomn[n]==key_sort){
            param_sort =='asc'? Clone.children[1].style.display ='flex':Clone.children[2].style.display ='flex'
        }
        Clone.style.display = 'flex'
        Clone.id = `key__${name_colomn[n]}`

        Clone.children[0].innerText = column_translations[name_colomn[n]]
        Parent.appendChild(Clone)
    }

    
    clonerows(name_colomn, rows_table )

    // клонирование строк  
    // Searcitem('')

    
}

function normalizeColumns(cols) {
    const priority = ['id', 'id_row'];

    const first = priority.filter(c => cols.includes(c));
    const rest  = cols.filter(c => !priority.includes(c));

    return [...first, ...rest];
}


function clonerows(name_colomn, rows_table){
    var Parent = document.getElementById('blockProdEquipment')
    ClearBlock(Parent, 1)
    var Children = Parent.children[0]
    
    var min_i = Page_main*maxInpage - maxInpage
    for (var i = min_i; i < rows_table.length; i++) {
        if (i >= maxInpage*Page_main) { break; }
        
        var Clone = Children.cloneNode(true);
        Clone.style.display = 'flex';
        Clone.id = `valuesTableRows_${i}`;
        // Clone.style = 'display: flex; flex-direction: column; align-items: flex-start; justify-content: center; width: 100%;'

        let colomnParent = Clone.children[0];
        ClearBlock(colomnParent, 2);
        var colomnChildren = colomnParent.children[1];
        
        let current_name_id_row = Object.keys(rows_table[i]).includes('id') ? 'id' : 'id_row';
        let current_id_row = rows_table[i][current_name_id_row];
        Clone.children[0].children[0].children[0].id = `CheckdoxTableRows_${current_id_row}`

        // Заполняем колонки
        for (var n = 0; n < name_colomn.length; n++) {
            if (!choice_colomn.includes(name_colomn[n])) { continue; }
            
            let colomnClone = colomnChildren.cloneNode(true);
            colomnClone.style.display = 'flex';
            colomnClone.id = `valuesTableRowsColomn_${n}`;
            rows_table[i][name_colomn[n]] ==null ? rows_table[i][name_colomn[n]] = '': 0


            text = rows_table[i][name_colomn[n]].length >=100 ? `${rows_table[i][name_colomn[n]].slice(0,25)}...` : rows_table[i][name_colomn[n]]
            typeof rows_table[i][name_colomn[n]] == 'object' ? text = objectToString(rows_table[i][name_colomn[n]]) : 0
            if(typeof(text) == 'string'){
                text = text.replace(/","/g, '", "')
            }
            colomnClone.children[0].innerText = text;
            colomnParent.appendChild(colomnClone);
            (function(row_id, row_name_id) {
                colomnClone.addEventListener("click", function() {
                    openWindowInfo(row_id, row_name_id);
                });
            })(current_id_row, current_name_id_row);
        }
        Parent.appendChild(Clone);
    }
    
}
function ClearBlock(TegParent, index){
    //   document.getElementById(parent).style.display = 'none'

  for (var n = TegParent.children.length-1; n >= index; n--) {
      TegParent.children[n].remove()
  }
}
function ClearTableinfo(){
   var Parent = document.getElementById('filter_block')
    ClearBlock(Parent, 1)

     var Parent = document.getElementById('selectionBlock')
    ClearBlock(Parent, 1)

      var Parent = document.getElementById('allProds')
    ClearBlock(Parent, 2)

    var Parent = document.getElementById('blockProdEquipment')
    ClearBlock(Parent, 1)
}
function remove_and_back(id){
    tableProducts.innerText = 'Список таблиц'
    buttonCreate.style.display = 'none';
    searchBar.style.display = 'none';
    DeleteEl = []
    windowAllTables.style.display = 'flex';
    windowAllProds.style.display = 'none';
    SearcitemBlock.value = ''
    
    Startmain_table()
    document.getElementById(id).remove()
    ClearTableinfo()

}


function Searcitem(value) {
    filtered_sorted_rows = searchInData(Choice_table['List_table'], value);
    infoblockNumderPage.innerText = `Всего строк: ${filtered_sorted_rows.length}`;
    clonerows(name_colomn, filtered_sorted_rows);
}


function clearsearc(){
    document.querySelector('.search-bar input').value = '';
    filtered_sorted_rows = Choice_table['List_table'];
    infoblockNumderPage.innerText = `Всего строк: ${filtered_sorted_rows.length}`;
    clonerows(name_colomn, filtered_sorted_rows);
}


function searchInData(data, searchQuery) {
     // Приводим поисковый запрос к нижнему регистру для регистронезависимого поиска
    const query = searchQuery.toString().toLowerCase().trim();
    
    // Ищем во всех объектах
    return data.filter(item => {
        // Проверяем все значения в объекте
        return Object.values(item).some(value => {
            if (value === null || value === undefined) {
                return false;
            }
            
            // Приводим значение к строке и нижнему регистру
            const strValue = value.toString().toLowerCase();
            
            // Проверяем, содержит ли значение поисковый запрос
            return strValue.includes(query);
        });
    });
}


function select_colomn(id){
    let Block = document.getElementById(id)
    Block.children[0].checked = !Block.children[0].checked
    name_Block = Block.children[1].id
    choice_colomn.includes(name_Block) ? choice_colomn = choice_colomn.filter(function(f) {return f!= name_Block}) : choice_colomn.push(name_Block)
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


function OldPage() {
    DeleteEl = [];

    let currentPage = Number(document.getElementById('Page_select_table').innerText.split(' ')[1]);

    if (currentPage <= 1) {
        BadToast('Вы уже на первой странице');
        return;
    }

    currentPage -= 1;
    Page_main = currentPage;
    document.getElementById('Page_select_table').innerText = `Страница ${currentPage}`;

    Clone_el_table({'List_table': filtered_sorted_rows, 'Info_table': Choice_table['Info_table']}, true);
}

function NextPage() {
    DeleteEl = [];

    let currentPage = Number(document.getElementById('Page_select_table').innerText.split(' ')[1]);
    
    // считаем количество страниц по filtered_sorted_rows
    let maxPage = Math.ceil(filtered_sorted_rows.length / maxInpage);

    if (currentPage >= maxPage) {
        BadToast('Дальше страниц нет');
        return;
    }

    currentPage += 1;
    Page_main = currentPage;
    document.getElementById('Page_select_table').innerText = `Страница ${currentPage}`;

    Clone_el_table({'List_table': filtered_sorted_rows, 'Info_table': Choice_table['Info_table']}, true);
}

function ChangeMaxRow(){
    maxInpage = document.getElementById('Select_maxRows').value
    Page_main =  1
    Clone_el_table({'List_table': filtered_sorted_rows, 'Info_table': Choice_table['Info_table']}, true);
}

var CheckedRows= []
function CheckedallProds(){
    var Parent = document.getElementById('blockProdEquipment')
    !allProds_input.checked ? DeleteEl = []:0
    for (var i = 1; i < Parent.children.length; i++) {
        Parent.children[i].children[0].children[0].children[0].checked = allProds_input.checked
        allProds_input.checked ? DeleteEl.push(Number(Parent.children[i].children[0].children[0].children[0].id.split('_')[1])) : DeleteEl = []
    }

}




function Change_el_info(id){
    var ID_M = id.split('_')[1]
    var key_id =Object.keys(el_row).includes('id')? 'id' :'id_row'

    document.getElementById(`changeInfo_${ID_M}`).style.display = 'none'
        document.getElementById(`savechangeInfo_${ID_M}`).style.display = 'flex'

    document.getElementById(`cancelchangeInfo_${ID_M}`).style.display = 'flex'
    var Parent = document.getElementById(`WindowInfo_${ID_M}`).getElementsByClassName('generalInfo')[0]

    for (var i = 1; i < Parent.children.length; i++) {
        if(Parent.children[i].children[1].id == key_id){
            continue
        }

        Parent.children[i].children[1].removeAttribute('readonly')

        Parent.children[i].children[1].classList.add('dopstyleParName')
    }


}

function Close_Change_el_info(id){
    var ID_M = id.split('_')[1]
    document.getElementById(`changeInfo_${ID_M}`).style.display = 'flex'
    document.getElementById(`savechangeInfo_${ID_M}`).style.display = 'none'

    document.getElementById(`cancelchangeInfo_${ID_M}`).style.display = 'none'

    var Parent = document.getElementById(`WindowInfo_${ID_M}`).getElementsByClassName('generalInfo')[0]


    for (var i = 1; i < Parent.children.length; i++) {
        if(typeof(el_row[ Parent.children[i].children[1].id])=='object'){
            Parent.children[i].children[1].value = objectToString(el_row[ Parent.children[i].children[1].id])
        }else{
            Parent.children[i].children[1].value = el_row[ Parent.children[i].children[1].id]
        }
        Parent.children[i].children[1].setAttribute('readonly', 'true')
        Parent.children[i].children[1].classList.remove('dopstyleParName')
        // Parent.children[i].children[1].style = 'border: solid 0px #878787; border-radius: 0px; height: 30px; padding-left: 0px;'
    }

}

function Save_change_el_info(id){
    var ID_M = id.split('_')[1]

    document.getElementById(`changeInfo_${ID_M}`).style.display = 'flex'
    document.getElementById(`savechangeInfo_${ID_M}`).style.display = 'none'

    document.getElementById(`cancelchangeInfo_${ID_M}`).style.display = 'none'
    var Parent = document.getElementById(`WindowInfo_${ID_M}`).getElementsByClassName('generalInfo')[0]

    for (var i = 1; i < Parent.children.length; i++) {
        console.log(Parent.children[i].children[1].id)
        if(typeof( el_row[ Parent.children[i].children[1].id]) =='object' && Array.isArray(el_row[ Parent.children[i].children[1].id])==true){
           el_row[ Parent.children[i].children[1].id] = Parent.children[i].children[1].value.split(',').map(item => item.trim());
        }
        if(typeof( el_row[ Parent.children[i].children[1].id]) =='object' && Array.isArray(el_row[ Parent.children[i].children[1].id])==false){

           el_row[ Parent.children[i].children[1].id] = JSON.parse(Parent.children[i].children[1].value);
        }
        if(typeof( el_row[ Parent.children[i].children[1].id]) =='string' ){
            el_row[ Parent.children[i].children[1].id] = Parent.children[i].children[1].value
        }
       if (typeof (el_row[Parent.children[i].children[1].id]) === 'number') {

            const input = Parent.children[i].children[1].value;

            const raw = input
                .replace(/\s/g, '')   // удалить ВСЕ пробелы
                .replace(',', '.');   // заменить запятую на точку

            const num = parseFloat(raw);

            if (!Number.isNaN(num)) {
                el_row[Parent.children[i].children[1].id] =
                    Math.round(num * 100) / 100; // округление до 2 знаков
            } else {
                el_row[Parent.children[i].children[1].id] = null;
            }
        }



        Parent.children[i].children[1].setAttribute('readonly', 'true')
        Parent.children[i].children[1].classList.remove('dopstyleParName')

        // Parent.children[i].children[1].style = 'border: solid 0px #878787; border-radius: 0px; height: 30px; padding-left: 0px;'

    }
    var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'
    var index = Choice_table['List_table'].indexOf(el_row)

    var table_name = table['name_table_db']

    DataList={
        'table_name':table_name ,
        'row':el_row,
        'key': key_id,
    }

    console.log(DataList)
    formData = JSON.stringify( DataList);
    $.ajax({
        url:`/off_bot/main_admin/Update_row`,
        data: formData,
        type: 'post',
        success: function (data) {
            Choice_table['List_table'][index] = el_row

            GoodToast('Изменения сохранены')
        },
        error: function (error) {
            Error_Message(`Update_row`)
        } 
    });

}


function Change_eladdit_info(){
    Closeadd_addit_info()
    document.getElementById(`change_addit_info`).style.display = 'none'
    document.getElementById(`saveadditchangeInfo`).style.display = 'flex'

    document.getElementById(`cancelchange_addit_info`).style.display = 'flex'
    var Parent = document.getElementById(`characteristicInfo`)
    for (var i = 1; i < Parent.children.length; i++) {
        Parent.children[i].children[0].children[1].removeAttribute('readonly')
        Parent.children[i].children[0].children[1].classList.add('inputborder')
    }

   
}
function Close_eladdit_info(){
    document.getElementById(`change_addit_info`).style.display = 'flex'
    document.getElementById(`saveadditchangeInfo`).style.display = 'none'
    document.getElementById(`cancelchange_addit_info`).style.display = 'none'
    var Parent = document.getElementById(`characteristicInfo`)
    for (var i = 1; i < Parent.children.length; i++) {
        id_additRow = Parent.children[i].id.split('_')[1]
        Parent.children[i].children[0].children[1].value =  dop_row.filter(function(f) {return f['id_row']== id_additRow})[0]['value']
        Parent.children[i].children[0].children[1].setAttribute('readonly', 'true')
        Parent.children[i].children[0].children[1].classList.remove('inputborder')
    }
}



function Save_change_eladdit_info(){
    document.getElementById(`change_addit_info`).style.display = 'flex'
    document.getElementById(`saveadditchangeInfo`).style.display = 'none'
    document.getElementById(`cancelchange_addit_info`).style.display = 'none'
    
    var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'
    var Parent = document.getElementById(`characteristicInfo`)
    for (var i = 1; i < Parent.children.length; i++) {
        id_additRow = Parent.children[i].id.split('_')[1]
        additional_parameters.filter(function(f) {return f['id_row']== id_additRow})[0]['value'] = Parent.children[i].children[0].children[1].value
        Parent.children[i].children[0].children[1].setAttribute('readonly', 'true')
        Parent.children[i].children[0].children[1].classList.remove('inputborder')
    }

    dop_row = additional_parameters.filter(function(f) {return f['type_machine']== TypeMAchine[table['name_table_db']] && f['id']== el_row[key_id] })





    DataList={
        'table_name':'additional_parameters' ,
        'row':dop_row,
        'key': 'id_row',
    }

    
 formData = JSON.stringify( DataList);
    $.ajax({
        url:`/off_bot/main_admin/Update_rows`,
        data: formData,
        type: 'post',
        success: function (data) {
            GoodToast('Изменения сохранены')
        },
        error: function (error) {
            Error_Message(`Update_rows`)
        } 
    });
}


function Deleteadditinfo(id){
    var ID_M = Number(id.split('_')[1])



    
    DataList={
        'table_name':'additional_parameters' ,
        'id_row':ID_M,
        'key': 'id_row',
    }

    formData = JSON.stringify( DataList);
    $.ajax({
        url:`/off_bot/main_admin/Delete_row`,
        data: formData,
        type: 'post',
        success: function (data) {
            additional_parameters = additional_parameters.filter(function(f) {return f['id_row']!= ID_M})
            var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'

            renderAdditionalCharacteristics(el_row,key_id )

        },
        error: function (error) {
            Error_Message(`Delete_row`)
        } 
    });


}

var DeleteEl = []
function ChoiceDeleteEl(id){
    var ID_M = Number(id.split('_')[1])
    DeleteEl.includes(ID_M) ?  DeleteEl = DeleteEl.filter(function(f) {return f!= ID_M}) : DeleteEl.push(ID_M)
}

function Delete_dataEl(){
    var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'
    var table_name = table['name_table_db']
    var id_row = el_row[key_id]


    Choice_table['List_table'] = Choice_table['List_table'].filter(function(f) {return f[key_id]!= id_row})


    DataList={
        'table_name':table_name ,
        'id_row':id_row,
        'key': key_id,
    }

    formData = JSON.stringify( DataList);
    $.ajax({
        url:`/off_bot/main_admin/Delete_row`,
        data: formData,
        type: 'post',
        success: function (data) {
            Choice_table['List_table'] = sortByKey(Choice_table['List_table'], key_sort,param_sort)
            Searcitem('')

            closeCrossBlockInfo()
            Clone_el_table(Choice_table, true)
        },
        error: function (error) {
            Error_Message(`Delete_row`)
        } 
    });
}


function Delete_data_arr(){
    if(DeleteEl.length == 0){
        WarningToast('Выберете строки для удаления')
        return
    }
    var key_id = Object.keys(Choice_table['List_table'][0]).includes('id')? 'id' :'id_row'
    var table_name = table['name_table_db']

    Choice_table['List_table'] = Choice_table['List_table'].filter(function(f) {return !DeleteEl.includes(f[key_id])})


    DataList={
        'table_name':table_name ,
        'id_row':DeleteEl,
        'key': key_id,
    }
    formData = JSON.stringify( DataList);
    $.ajax({
        url:`/off_bot/main_admin/Delete_row_arr`,
        data: formData,
        type: 'post',
        success: function (data) {
            
            delete_add_params = additional_parameters
                .filter(f =>
                    f['type_machine'] === TypeMAchine[table['name_table_db']] &&
                    DeleteEl.includes(Number(f['id']))
                )
                .map(f => f['id_row']);
            if( additional_parameters.length != 0){
                DataList={
                    'table_name':'additional_parameters' ,
                    'id_row':delete_add_params,
                    'key': 'id_row',
                }
                formData = JSON.stringify( DataList);
                $.ajax({
                    url:`/off_bot/main_admin/Delete_row_arr`,
                    data: formData,
                    type: 'post',
                    success: function (data) {
                       additional_parameters = additional_parameters.filter(function(f) {return delete_add_params.includes(f['id_row']) == false })

                        console.log('удалили не нужные  параметры')
                    },
                    error: function (error) {
                        Error_Message(`Delete_row_arr`)
                    } 
                });
            }
            
            DeleteEl = []
            Choice_table['List_table'] = sortByKey(Choice_table['List_table'], key_sort,param_sort)
            Searcitem('')

            Clone_el_table(Choice_table, true)
        },
        error: function (error) {
            Error_Message(`Delete_row_arr`)
        } 
    });


}

function Save_dataEl(){
    var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'
    var table_name = table['name_table_db']
    var id_row = el_row[key_id]

    var index = Choice_table['List_table'].indexOf(el_row)

    var id_block = table['access_level'] == '1' ? 'generalInfo' : 'generalInfoTwo'
    var Parent = document.getElementById(id_block)
    for (var i = 1; i < Parent.children.length; i++) {
        if(Parent.children[i].children[1].id == 'id_row' || Parent.children[i].children[1].id == 'id'){
            continue
        }
        el_row[ Parent.children[i].children[1].id] = Parent.children[i].children[1].value

    }

    Choice_table['List_table'][index] = el_row
    DataList={
        'table_name':table_name ,
        'row':el_row,
        'key': key_id,
    }

    Update_row(DataList)
}

function Update_row(DataList){
   formData = JSON.stringify( DataList);
    $.ajax({
        url:`/off_bot/main_admin/Update_row`,
        data: formData,
        type: 'post',
        success: function (data) {
            Choice_table['List_table'] = sortByKey(Choice_table['List_table'], key_sort,param_sort)

        },
        error: function (error) {
            Error_Message(`Update_row`)
        } 
    });
}
function New_dataEl(){
    var table_name = table['name_table_db']
    el_row = {...Choice_table.List_table[0]};
    var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'
    maxID = Number(findMaxByKey(Choice_table['List_table'], key_id))
    console.log(maxID)
    el_row[key_id] = maxID+1
    console.log(el_row)
    el_row= resetAllValues(el_row, [key_id, "date"])
    DataList={
        'table_name':table_name ,
        'row':el_row,
    }

    formData = JSON.stringify( DataList);
    $.ajax({
        url:`/off_bot/main_admin/Insert_row`,
        data: formData,
        type: 'post',
        success: function (data) {
            Choice_table['List_table'].push(data)
            Choice_table['List_table'] = sortByKey(Choice_table['List_table'], key_sort,param_sort)

            Searcitem('')
            Clone_el_table(Choice_table, true)

            openWindowInfo(el_row[key_id],key_id )
        },
        error: function (error) {
            Error_Message(`Insert_row`)
        } 
    });


}
var new_ad_row = ''
function add_addit_info(){
    Close_eladdit_info()
    blockPermanentChar.style.display = 'flex'
    maxID = Number(findMaxByKey(additional_parameters, 'id_row'))
    var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'

    new_ad_row = {
        "id_row":  maxID+1,
        "id": String(el_row[key_id]),
        "id_bitrix": '',
        "parameter_name": "",
        "value": "",
        "unit_of_measurement": "",
        "type_machine": TypeMAchine[table['name_table_db']],
        "type": "offer",
        "language": el_row['language']
    }
    console.log(new_ad_row)
}

function Closeadd_addit_info(){
    blockPermanentChar.style.display = 'none'
    new_ad_row = ''
}

function SaveNewRow_addit_info(){
    if(document.getElementById('addit_parameter_name').value==''){
        WarningToast('Введите наименование параметра')
        return
    }
    if(document.getElementById('addit_value').value==''){
        WarningToast('Введите значение параметра')
        return
    }
    var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'

    new_ad_row['value'] = document.getElementById('addit_value').value
    new_ad_row['parameter_name'] = document.getElementById('addit_parameter_name').value
    new_ad_row['unit_of_measurement'] = document.getElementById('addit_unit_of_measurement').value
    new_ad_row['id_bitrix'] = document.getElementById('addit_BitrixId').value

    DataList={
        'table_name':'additional_parameters' ,
        'row':new_ad_row,
    }

    formData = JSON.stringify( DataList);
    $.ajax({
        url:`/off_bot/main_admin/Insert_row`,
        data: formData,
        type: 'post',
        success: function (data) {
            document.getElementById('addit_value').value = ''
            document.getElementById('addit_parameter_name').value = ''
            document.getElementById('addit_unit_of_measurement').value = ''
            document.getElementById('addit_BitrixId').value = ''

            additional_parameters.push(new_ad_row)
            new_ad_row = ''
            add_addit_info()
            renderAdditionalCharacteristics(el_row,key_id )
        },
        error: function (error) {
            Error_Message(`Insert_row`)
        } 
    });
}


function resetAllValues(obj, exceptions = []) {
  const result = Array.isArray(obj) ? [...obj] : { ...obj };

  for (const key in result) {
    // Пропускаем исключения
    if (exceptions.includes(key)) continue;

    const value = result[key];

    // Обнуляем в зависимости от типа
    switch (typeof value) {
      case "number":
        result[key] = 0;
        break;
      case "string":
        result[key] = "";
        break;
      case "boolean":
        result[key] = false;
        break;
      case "object":
        if (value === null) {
          result[key] = null;
        } else if (Array.isArray(value)) {
          result[key] = [];
        } else {
          result[key] = resetAllValues(value, exceptions); // Рекурсия для вложенных объектов
        }
        break;
      default:
        result[key] = null; // undefined, function, symbol и др.
    }
  }

  return result;
}



function SortByKey_Func(id) {
    var ID_M = id.split('__')[1];

    if (key_sort === ID_M) {
        param_sort = param_sort === 'asc' ? 'desc' : 'asc';
    } else {
        param_sort = 'asc';
        key_sort = ID_M;
    }

    filtered_sorted_rows = sortByKey(filtered_sorted_rows, key_sort, param_sort);

    Clone_el_table({
        'List_table': filtered_sorted_rows,
        'Info_table': Choice_table['Info_table']
    }, false);
}



function Changephoto(){

  document.getElementById("fileElem").value = ''
  var el = document.getElementById("fileElem");
  if (el) {
    el.click();
  }
}

function handleFiles(files_photo, id) {
    var files_photo = document.getElementById(`fileElem`).files
    TypeForm = new FormData();
    TypeForm.append(`file`, files_photo[0], ID_USER)

    ToglCheckAnalys = true
    var key_id = Object.keys(el_row).includes('id')? 'id' :'id_row'

    el_row['photo']!= ''? namephoto = el_row['photo'].replace('.png','') : namephoto = `${table['name_table_db']}_${el_row[key_id]}`
    formData = TypeForm;
    var index = Choice_table['List_table'].indexOf(el_row)

  $.ajax({
    type: 'POST',
    url: `/off_bot/main_admin/SavePhoto/${namephoto}`,
    data: formData,
    processData: false,
    contentType: false,
    success: function(data){
      GoodToast('Фотография успешно загружена')
      console.log(data)
        el_row['photo']= data
        Choice_table['List_table'][index] = el_row
        document.getElementById("fileElem").value = ''

        framePhotoEquip.children[0].style.display = 'none'
        PhotoEquip.style.display = 'flex'
        PhotoEquip.src = `/off_bot/static/img_machine/${el_row['photo']}`
        
        DataList={
            'table_name':table['name_table_db'] ,
            'row':el_row,
            'key': key_id,
        }

    
        Update_row(DataList)

    },
    error: function (error) {
      Error_Message(`Manager_SavePhoto ${ID_USER}\n${error}`)
    } 
  })  
  
}

function findMaxByKey(data, key) {
    let maxValue = -Infinity;
    let found = false;

    // Перебираем все элементы в объекте data
    for (const itemId in data) {
        const item = data[itemId];
        
        // Проверяем, существует ли ключ в текущем элементе
        if (item && item.hasOwnProperty(key)) {
            const currentValue = item[key];
            
            // Сравниваем текущее значение с максимальным
            if (currentValue > maxValue) {
                maxValue = currentValue;
                found = true;
            }
        }
    }

    return found ? maxValue : null;
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
