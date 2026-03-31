
var tg, ID_USER,UserName, key = '', id_provider, data_CP , List_CP
var togl_check = false
pages = 'Separator'

default_data_CP = {
        'Sieve': {},
        'elevator' :{},
        'sep_machine': {},
        'compressor': {},
        'photo_sorter': {},
        'extra_equipment':{},
        'Service': {},
        'attendance': {},
        'Pneumatic_feed' :{},
        'laboratory_equipment':{}

    }
window.onload = async function() {
    await I18N.load(lang, 'common');

    tg = window.Telegram.WebApp;
    
    tg.disableVerticalSwipes()
    tg.expand(); //расширяем на все окно
    tg.MainButton.text = I18N.t('selectPhotoSorter'); //изменяем текст кнопки 
    tg.MainButton.textColor = "#fff"; //изменяем цвет текста кнопки
    tg.MainButton.color = "#e01818"; //изменяем цвет бэкграунда кнопки
    
    Telegram.WebApp.onEvent('mainButtonClicked', GetInfoSepar)

    // tg.MainButton.offClick(function() {
    //     // document.getElementById('ListFullData').style.display == 'none' && document.getElementById('UserInfo_Block').style.display == 'none' ? openUserInfoSepar() :0
    //     openUserInfoSepar()
    // })
    tg.MainButton.show() 
    // tg.BackButton.hide()
    href = window.location.href
    ID_USER =  new URL(href).searchParams.get('tg_id')
    UserName = new URL(href).searchParams.get('username')

    new URL(href).searchParams.get('keyCP')!= null? ( key = new URL(href).searchParams.get('keyCP'), getKP_info()) : writeNewCP('Separator')
    // key =   writeNewCP('Separator')

    getProd_list()

}
var Separ_perf = [], Compressor_perf = [], List_separ=[], List_compressor= [], List_equipment=[], List_gost = []

function DeleteChildren(Parent){
    for (var n = Parent.children.length-1; n > 0; n--) {Parent.children[n].remove()}
}

function getProd_list(){
    List = 'calc_sieve'

    $.ajax({
        url: `/off_bot/API/getListData_Separ/${lang}`,
        type: 'get',
        success: function (data) {
            Separ_perf = data['Separ_perf']
            Compressor_perf = data['Compressor_perf']
            List_separ = data['List_separ'].sort((a, b) => a.id_row - b.id_row);
            List_compressor = data['List_compressor']
            List_equipment = data['List_equipment']
            
            List_gost= data['List_gost']

            // getСonditions_list()
            Get_prod()
            chooseProduct.value = 'Пшеница'
            Choice_Prod('Пшеница')
            choosePurpose.value = 'Семена'
            Choice_Purpose('Семена')
          },
          error: function (error) {
            Error_Message(`getListData ${ID_USER}\n${error}`)
          }
    });
}

function getUniqueProducts(data) {
    const uniqueProducts = new Set();
    data.forEach(item => {
        uniqueProducts.add(item.product);
    });
    return Array.from(uniqueProducts);
}

function Get_prod(){
    let Parent = document.getElementById('chooseProduct')
    DeleteChildren(Parent)
    let Children = Parent.children[0]
    const Prod_list = getUniqueProducts(Separ_perf);
    for(var i = 0; i< Prod_list.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.disabled = false
        Clone.innerText = Prod_list[i]
    
        Parent.appendChild(Clone)
    }



}
function getUniqueForArry(data, json_key) {
    const unique= new Set();
    data.forEach(item => {
        item[json_key].forEach(garbageItem => {
            unique.add(garbageItem);
        });
    });
    return Array.from(unique);
}
var Product, Purpose, Garbage
function getSeparatorInputValues() {
    return {
        sor: Number(inputInitialClog.value),
        qual: Number((inputRequiredQuality.value / 100).toFixed(2)),
        qualPercent: Number(inputRequiredQuality.value),
        performance: Number(String(inputEfficiency.value).replace(',', '.'))
    };
}

function validateSeparatorInputValues(values) {
    if (!values || !values.sor || !values.qual || !values.performance) {
        BadToast(I18N.t('enterAllValues'));
        return false;
    }
    if (values.sor < 100 - values.qual * 100) {
        BadToast(I18N.t('qualityError'));
        return false;
    }
    return true;
}

function postSeparatorRequest(url, payload, successHandler, errorLabel) {
    $.ajax({
        url: url,
        data: JSON.stringify(payload),
        type: 'post',
        success: successHandler,
        error: function(error) {
            Error_Message(`${errorLabel} ${ID_USER}
${error}`)
        }
    });
}

function getSelectedSeparatorChoice() {
    return Separ_perf.filter(function(f) {
        return f['product'] == Product && f['purpose'] == (Purpose)
    })[0]
}

function Choice_Prod(value){
    Product = value
    List_choice_garabage = []
    inputEfficiency.value = ''
    inputRequiredQuality.value = ''
    inputInitialClog.value = ''
    Purpose = ''
    Garbage = ''
    let Parent = document.getElementById('choosePurpose')
    DeleteChildren(Parent)
    let Children = Parent.children[0]

    List_purpose = Separ_perf.filter(function(f) { return f['product'] == Product})
    for(var i = 0; i< List_purpose.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.innerText = List_purpose[i]['purpose'][0]
        Clone.disabled = false
        Parent.appendChild(Clone)
        i==0? first_purp = List_purpose[i]['purpose'][0] :0
    }
    
    purposeBlock.style.filter = 'none'
    purposeBlock.style.pointerEvents = 'auto'
    choosePurpose.value = I18N.t('selectPurpose')

    clogBlock.style.filter = 'blur(2px)'
    clogBlock.style.pointerEvents = 'none'
    Block_indicators.style.filter = 'blur(2px)'
    Block_indicators.style.pointerEvents = 'none'

    Block_result.style.display = 'none'
    DeleteChildren(document.getElementById('clasifierClogs'))
    
    let ParentGost = document.getElementById('GoltBlock')
    for (var n = ParentGost.children.length-1; n > 1; n--) {ParentGost.children[n].remove()}

    document.getElementById('choosePurpose').value=first_purp
    Choice_Purpose(first_purp)
}

function Choice_Purpose(value){
    Purpose = value
    List_choice_garabage = []
    inputEfficiency.value = ''
    inputRequiredQuality.value = ''
    inputInitialClog.value = ''
    Garbage = ''
    let Parent = document.getElementById('clasifierClogs')
    DeleteChildren(Parent)
    let Children = Parent.children[0]
    List_garbage = getUniqueForArry(Separ_perf.filter(function(f) { return f['product'] == Product && f['purpose'] == Purpose }), 'garbage')
    clogBlock.style.filter = 'none'
    clogBlock.style.pointerEvents = 'auto'
    Block_indicators.style.filter = 'blur(2px)'
    Block_indicators.style.pointerEvents = 'none'
    for(var i = 0; i< List_garbage.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        Clone.id = `Garbage_${i}`
        Clone.children[1].innerText = List_garbage[i]
        Parent.appendChild(Clone)
        Clone.click()
    }
    Block_result.style.display = 'none'

    El_gost = List_gost.filter(function(f) { return f['product'] == Product && f['purpose'].includes(Purpose) })
    
    let ParentGost = document.getElementById('GoltBlock')
    for (var n = ParentGost.children.length-1; n > 1; n--) {ParentGost.children[n].remove()}
    let ChildrenGost = ParentGost.children[1]

    for(var i = 0; i< El_gost.length; i++){
        var CloneGost = ChildrenGost.cloneNode(true)
        CloneGost.style.display = 'flex'
        CloneGost.children[0].innerText = El_gost[i]['name']
        CloneGost.children[1].innerText = El_gost[i]['gost']
        CloneGost.children[1].href = El_gost[i]['link']
        ParentGost.appendChild(CloneGost)
    }
  

}
var List_choice_garabage = []
function Choice_Garbage(id){
    let value_id = document.getElementById(id).children[1].innerText
    if(List_choice_garabage.includes(value_id)){
        List_choice_garabage = List_choice_garabage.filter(function(f) { return f != value_id})
    }
    else{
        List_choice_garabage.push(value_id)
    }
    document.getElementById(id).children[0].checked = !document.getElementById(id).children[0].checked

    if(List_choice_garabage.length == 0){
        Block_indicators.style.filter = 'blur(2px)'
        Block_indicators.style.pointerEvents = 'none'
        return
    }
   
    Garbage = value_id

    Block_indicators.style.filter = 'none'
    Block_indicators.style.pointerEvents = 'auto'
    List_Depfotl = Separ_perf.filter(function(f) { return f['product'] == Product && f['purpose'] == (Purpose)  })[0]


    inputInitialClog.value = List_Depfotl['garbage_percentage'].toFixed(2)

    inputRequiredQuality.value = List_Depfotl['quality_percentage'].toFixed(2)
    
    El_row = Separ_perf.filter(function(f) { return f['product'] == Product && f['purpose']== (Purpose)  })[0]
    inputEfficiency.value = Product =='Кофе' ?(El_row['performance_tray_per_t_h']).toFixed(1) : (El_row['performance_tray_per_t_h']*3).toFixed(1)
}
var El_choice = ''
async function return_Result_air(El_choice, togl, count_tray){
    var values = getSeparatorInputValues()

    if(togl && count_tray){
        Count_tray = Math.ceil(Number((values.performance / El_choice['performance_tray_per_t_h'])), 1) 
    }
    else{
        Count_tray = totalValue(data_CP['group_info']['photo_sorter'])
    }

    var DataList = {
        'sor': values.sor,
        'qual' : values.qualPercent,
        'performance' : values.performance,
        'Count_tray'  : Count_tray ,
        'El_choice' : El_choice
    }
    console.log(DataList)
    
    postSeparatorRequest('/off_bot/API_CALC/Result_air', DataList, function(data) {
        console.log('off_bot/API_CALC/Result_air', data)
        if(togl && count_tray){
            loadAndRenderSeparators(Number(data['Result_air']), Number(data['air_flow_per_tray']))
        }
        else{
            loadAndRenderSeparators(Number(data['Result_air']), Number(data['air_flow_per_tray']), data_CP['group_info']['photo_sorter'])
        }
    }, 'calculate_air')
}

async function GetInfoSepar(){
    document.getElementById('saveInfo').style.display = 'flex'
    Telegram.WebApp.offEvent('mainButtonClicked', GetInfoSepar)
    Telegram.WebApp.onEvent('mainButtonClicked', openUserInfoSepar)
    tg.MainButton.text = I18N.t('getKP');
    tg.MainButton.show() 

    resetObject(data_CP['group_info'], default_data_CP);
    El_choice = getSelectedSeparatorChoice()

    var values = getSeparatorInputValues()
    if(!validateSeparatorInputValues(values)){
        return
    }

    return_Result_air(El_choice, true, true);
}

function renderSeparatorUI(data, Result_air, air_flow_per_tray, performance, togl) {

    let Parent = document.getElementById('infoSepar')
    DeleteChildren(Parent)
    let Children = Parent.children[0]
    Block_result.style.display = 'flex'
    // Count_tray = Math.ceil(Number((performance/El_choice['performance_tray_per_t_h'])), 1) 

    const loop = Object.keys(data).length
    for(let i = 0; i < loop; i++) {
        Count_tray = data[i]['loop_tray']
        count_separ = data[i]['count_separ']
        // const count_separ = Count_tray >= 8 ? Math.ceil(Count_tray/8) : 1;
        
        if(togl!=undefined){
            var Separators = List_separ.filter(function(f) { return Object.keys(data_CP['group_info']['photo_sorter']).includes(String(f['id_row']))  })
        }
        else{
            var Separators = List_separ.filter(function(f) { return f['tray'] == Count_tray && (f['configuration'] == data[i]['El_choice']['sep_config']) })
        }

        const Clone = Children.cloneNode(true);
        Clone.style.display = 'flex';

        const Parent2 = Clone.children[1].children[0].children[1];
        Parent2.id = `modelSepar_${i}`;
        List_modelSep = List_separ.filter(function(f) { return f['configuration'] == El_choice['sep_config'] || f['configuration'] == I18N.t('noConfiguration')  })

        List_modelSep.forEach((model, n) => {
            const Clone2 = Parent2.children[0].cloneNode(true);
            Clone2.style.display = 'flex';
            Clone2.innerText = model.name_print.replace(I18N.t('photoSorterPrefix'),'');
            
            if(Separators.filter(f => f.name_print === model.name_print).length !== 0) {
                Clone2.style.backgroundColor = '#92cbee';
            }
            
            Clone2.disabled = false;
            Parent2.appendChild(Clone2);
            
            if(Separators.filter(f => f.name_print === model.name_print).length !== 0) {
                if(Parent2.value === '') {
                    if(Product === 'Кофе' && performance <= 0.8) {
                        if(model.model_series.includes('L')) {
                            updateValues();
                        }
                    } else {
                        updateValues();
                    }
                    
                    function updateValues() {
                        Parent2.value = model.name_print.replace(I18N.t('photoSorterPrefix'), '');
                        data_CP.group_info.photo_sorter[model.id_row] = Number(count_separ.toFixed(0));
                    }
                }
            }
        });

        const Parent3 = Clone.children[1].children[1].children[1];
        Parent3.id = `configurationSepar_${i}`;
        
        const List_config = [...new Set(List_separ.map(item => item.configuration))];
        List_config.forEach(config => {
            if(config === I18N.t('noConfiguration')) return;
            
            const Clone3 = Parent3.children[0].cloneNode(true);
            Clone3.style.display = 'flex';
            Clone3.innerText = config;
            
            if(Separators.filter(f => f.configuration === config).length !== 0) {
                Clone3.style.backgroundColor = '#92cbee';
            }
            
            Clone3.disabled = false;
            Parent3.appendChild(Clone3);
            
            if(Separators.filter(f => f.configuration === config).length !== 0) {
                if(Parent3.value === '') {
                    Parent3.value = config;
                }
            }
        });

        Clone.children[1].children[2].innerText = `${I18N.t('performance')}: ${(El_choice.performance_tray_per_t_h*Count_tray).toFixed(1)} ${I18N.t('tonsPerHour')}`


        Clone.children[1].children[3].children[1].children[0].id = `Separ_minus_${i}`;
        Clone.children[1].children[3].children[1].children[1].id = `Separ_input_${i}`;
        Clone.children[1].children[3].children[1].children[1].value = count_separ.toFixed(0);
        Clone.children[1].children[3].children[1].children[2].id = `Separ_plus_${i}`;

        Parent.appendChild(Clone);
    }


    togl_check = true
    GetDop_equipment(data, Result_air, air_flow_per_tray)
    
    Scroll_startBlock(document.getElementById('Block_result'))


}
// Пример использования:
async function loadAndRenderSeparators(Result_air, air_flow_per_tray, choice_sorter) {
    var values = getSeparatorInputValues()
    if(!validateSeparatorInputValues(values)){
        return
    }

    const DataList = {
        'Product': Product,
        'Purpose': Purpose,
        'Count_tray': Count_tray,
        'performance': values.performance,
        'choice_sorter' :choice_sorter
    };
    console.log(DataList)

    try {
        postSeparatorRequest(`/off_bot/API_CALC/GetInfoSepar/${lang}`, DataList, function (data) {
            console.log('off_bot/API_CALC/GetInfoSepar', data)
            renderSeparatorUI(data, Result_air, air_flow_per_tray, values.performance, choice_sorter);
        }, 'calculate_air')
    } catch (error) {
        console.error('Error:', error);
        Error_Message(`calculate_air ${ID_USER}
${error}`);
    }
}


function totalValue(data){
    const totalValue = List_separ.reduce((sum, item) => {
        if (data[item.id_row]) { // Проверяем, есть ли id_row в ключах idRowMap
            return sum + item.tray*data[item.id_row]; // Если есть, добавляем значение value
        }
        return sum; // Если нет, ничего не добавляем
    }, 0);
    return totalValue
}
// максимально значение производительности компрессора
function getMaxPerf(data) {
    return Math.max(...data.map(item => item.max_perf));
}
function getMaxPerf_min(data) {
    return Math.max(...data.map(item => item.min_perf));
}
async function GetDop_equipment(data_equps, Result_air, air_flow_per_tray) {
    const Count_tray = totalValue(data_CP['group_info']['photo_sorter']);
    const requestData = {
        'Count_tray': Count_tray,
        'Result_air': Number(Number(Count_tray * air_flow_per_tray.toFixed(1)).toFixed(1)),
        'air_flow_per_tray': air_flow_per_tray,
        'Product': Product,
    };

    $.ajax({
        url: `/off_bot/API_CALC/calculate_compressor/${lang}`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(result) {
            console.log(result)
            if(result['equipment_ids']!= {}){
                data_equps[0]['dop_equipment'] = { ...data_equps[0]['dop_equipment'], ...result['equipment_data'] };
                data_equps[0]['group_info']['extra_equipment'] = { ...data_equps[0]['group_info']['extra_equipment'], ...result['equipment_ids'] };
            }

            var struc_data_equps = combineAllDopEquipment(data_equps)
            var arr_data_equps = sortDopEquipment(struc_data_equps)

            const Parent = document.getElementById('infoCompressor');
            DeleteChildren(Parent);
            const Children = Parent.children[0];
            
            result.compressors.forEach(function(compressorData) {
                const Compressor = compressorData.compressor;
                const Perf = compressorData.performance;
                const count = compressorData.count;
                
                let Clone = Children.cloneNode(true);
                Clone.style.display = 'flex';
                Clone.children[1].children[0].innerText = `${I18N.t('model')}: ${Compressor.name}`;
                Clone.children[1].children[1].innerText = `${I18N.t('performance')}: ${Perf.min_perf} - ${Perf.max_perf} ${I18N.t('litersPerMinute')} (${compressorData.air_flow.toFixed(1)})`
                Clone.children[1].children[2].innerText = `${I18N.t('quantity')}: ${count} ${I18N.t('pcs')}`;
                
                Parent.appendChild(Clone);
                data_CP['group_info']['compressor'][Compressor.id_row] = count;
            });
            
            if (result.warning) {
                WarningToast(result.warning);
            }
            
            const equipParent = document.getElementById('infoDopMachine');
            DeleteChildren(equipParent);
            const equipChildren = equipParent.children[0];
            
            for (let i = 0; i < arr_data_equps.length; i++) {
                const El_row = arr_data_equps[i];
                let Clone = equipChildren.cloneNode(true);
                Clone.style.display = 'flex';
                Clone.children[0].children[0].innerText = El_row.type;
                Clone.children[1].children[0].innerText = `${I18N.t('model')}: ${El_row.model}`;
                Clone.children[1].children[1].innerText = `${I18N.t('quantity')}: ${El_row.count} ${I18N.t('pcs')}`;
                equipParent.appendChild(Clone);
            }
            data_extra_equipment = combineExtraEquipment(data_equps)
            data_CP['group_info']['extra_equipment'] = data_extra_equipment
            data_CP['additional_info']['prod'] = Product;
            data_CP['additional_info']['efficiency'] = inputEfficiency.value;
            data_CP['additional_info']['purpose'] = Purpose;
            data_CP['additional_info']['garbage'] = List_choice_garabage;
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при расчете компрессоров:', error);
            ErrorToast(I18N.t('serverConnectionError'));
        }
    });
}


function combineExtraEquipment(data) {
  const result = {};

  // Перебираем все группы в данных
  Object.values(data).forEach(group => {
    if (!group.group_info || !group.group_info.extra_equipment) return;

    const extraEquipment = group.group_info.extra_equipment;

    // Перебираем все элементы extra_equipment в группе
    Object.entries(extraEquipment).forEach(([key, value]) => {
      // Если ключ уже есть в результате - суммируем значения
      if (result.hasOwnProperty(key)) {
        result[key] += value;
      } else {
        // Иначе просто добавляем
        result[key] = value;
      }
    });
  });

  return result;
}

function combineAllDopEquipment(data) {
  const result = [];

  // Перебираем все группы в данных
  Object.values(data).forEach(group => {
    if (!group.dop_equipment) return;

    // Обрабатываем оба формата: объект и массив
    if (Array.isArray(group.dop_equipment)) {
      // Добавляем элементы массива
      result.push(...group.dop_equipment);
    } else if (typeof group.dop_equipment === 'object' && group.dop_equipment !== null) {
      // Добавляем значения объекта
      Object.values(group.dop_equipment).forEach(item => {
        result.push(item);
      });
    }
  });

  return result;
}


function sortDopEquipment(equipmentArray) {
  // Определяем порядок сортировки
  const sortOrder = {
    "Бункер": 1,
    "Сходы": 2,
    "Аспирация": 3,
    "Доп оборудование": 4
  };

  // Создаем копию массива, чтобы не изменять исходный
  const sortedArray = [...equipmentArray];

  // Сортируем массив по заданному порядку
  sortedArray.sort((a, b) => {
    const orderA = sortOrder[a.type] || 5; // 5 - для неизвестных типов (в конец)
    const orderB = sortOrder[b.type] || 5;
    return orderA - orderB;
  });

  return sortedArray;
}
function resetObject(target, template) {
  Object.keys(target).forEach(k => delete target[k]);
  Object.assign(target, structuredClone(template));
}


function Change_separ(id){
    resetObject(data_CP['group_info'], default_data_CP);

    let Parent_model= document.getElementById(id).value
    var ID_M = id.split('_')[1]

    if(Parent_model == 'MiniSort'){
        DeleteChildren(document.getElementById(`configurationSepar_${ID_M}`))
        let Parent = document.getElementById(`configurationSepar_${ID_M}`)
        let Children = Parent.children[0]
        let Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        Clone.innerText = I18N.t('noConfiguration')
        Parent.appendChild(Clone)
        document.getElementById(`configurationSepar_${ID_M}`).value = I18N.t('noConfiguration')
    }
        
    let Parent_config= document.getElementById(`configurationSepar_${ID_M}`).value

    Separator = List_separ.filter(function(f) { return f['configuration'] == Parent_config && f['name_print'].includes(Parent_model) })[0]
    El_row = Separ_perf.filter(function(f) { return f['product'] == Product && f['purpose'] == (Purpose)  })[0]

    document.getElementById(id).parentNode.parentNode.children[2].innerText = `${I18N.t('performance')}: ${(El_row['performance_tray_per_t_h'] * Separator['tray']).toFixed(1)} ${I18N.t('tonsPerHour')}`
    //    ПОДУМАТЬ
  
    let Parent = document.getElementById('infoSepar')
    for(var i = 1; i< Parent.children.length; i++){
        model = Parent.children[i].children[1].children[0].children[1].value
        config = Parent.children[i].children[1].children[1].children[1].value
        count  = Number(Parent.children[i].children[1].children[3].children[1].children[1].value)
        new_sep = List_separ.filter(function(f) { return f['configuration'] == config && f['name_print'].includes(model) })[0]
        data_CP['group_info']['photo_sorter'][new_sep['id_row']] = count
    }


    if(Parent_model == 'MiniSort'){
        Parent = document.getElementById('infoCompressor')
        DeleteChildren(Parent)
        infoCompressor.style.display = 'none'
        infoDopMachine.style.display = 'none'
    }
    else{
        return_Result_air(El_choice, false, false)
        infoCompressor.style.display = 'flex'
        infoDopMachine.style.display = 'flex'
    }
}

function Change_config(id){
    data_CP['group_info']['photo_sorter'] = {}

    let Parent = document.getElementById('infoSepar')
    for(var i = 1; i< Parent.children.length; i++){
        model = Parent.children[i].children[1].children[0].children[1].value
        config = Parent.children[i].children[1].children[1].children[1].value
        count  = Number(Parent.children[i].children[1].children[3].children[1].children[1].value)
        new_sep = List_separ.filter(function(f) { return f['configuration'] == config && f['name_print'].includes(model) })[0]
        data_CP['group_info']['photo_sorter'][new_sep['id_row']] = count
    }
}

function New_Garbage(){
    Botton_New_Garbage.style.display = 'none'
    BlockAddGarbage.style.display = 'flex'

}

function Add_Garbage(id){
    Botton_New_Garbage.style.display = 'flex'
    BlockAddGarbage.style.display = 'none'
    
    if(id=='close_garbage'){
        document.getElementById('New_Garbage').value = ''
        return
    }

    let value = document.getElementById('New_Garbage').value
    
    let Parent = document.getElementById('clasifierClogs')
    let len = Parent.children.length
    let Children  = Parent.children[0]
    var Clone = Children.cloneNode(true)
    Clone.style.display = 'flex'
    Clone.id = `Garbage_${len}`
    Clone.children[1].innerText = value
    Parent.appendChild(Clone)
    document.getElementById('New_Garbage').value = ''


}

function changeCountMinus_photosep(id){
    var ID_M = id.split('_')[2]
    if(document.getElementById(`Separ_input_${ID_M}`).value == 1){
        BadToast(I18N.t('invalidValue'))
        return
    }

    document.getElementById(`Separ_input_${ID_M}`).value =Number( document.getElementById(`Separ_input_${ID_M}`).value) - 1

    Change_separ(`modelSepar_${ID_M}`)
}
function changeCountPlus_photosep(id){
    var ID_M = id.split('_')[2]
    document.getElementById(`Separ_input_${ID_M}`).value =Number( document.getElementById(`Separ_input_${ID_M}`).value) + 1

    Change_separ(`modelSepar_${ID_M}`)

}



function openUserInfoSepar(){
    if(!togl_check){
        BadToast(I18N.t('makeCalculation'))
        return
    }
    UpdateCPlist(data_CP, List_CP, 'Separator')
}


function Input_change(id){
    document.getElementById(id).value =  document.getElementById(id).value.replace(',', '.')
    document.getElementById(id).value >100? (document.getElementById(id).value = 100, WarningToast(I18N.t('percentLimit'))) :0
}
function Input_change_Efficiency(id){
    document.getElementById(id).value =  document.getElementById(id).value.replace(',', '.')
}



function Plus_inputEfficiency(){
  inputEfficiency.value =  Number((Number(inputEfficiency.value) + 0.1).toFixed(1))
}
function Minus_inputEfficiency(){
  if(Number(inputEfficiency.value) <=0.1){
      BadToast(I18N.t('efficiencyMin'))
      return
  }
  inputEfficiency.value =  Number((Number(inputEfficiency.value) -  0.1).toFixed(1))
}


function Back_Open_Info(){
    if(clogBlock.style.display =='none'){
        clogBlock.style.display ='block'
        Block_indicators.style.display ='block'
        // Block_dop_info.style.marginBottom = '10px'
    }
    else{
        clogBlock.style.display ='none'
        Block_indicators.style.display ='none'
        // Block_dop_info.style.marginBottom = '0px'
    }
}