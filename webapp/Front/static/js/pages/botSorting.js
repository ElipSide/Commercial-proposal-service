var tg, ID_USER,UserName, key = '', id_provider, data_CP , List_CP, User_Info =''
pages = 'Sorting'
window.onload = function() {
    // document.getElementById('mainBlock').style.filter = 'blur(2px)'
    tg = window.Telegram.WebApp;
    tg.disableVerticalSwipes()
    tg.expand(); //расширяем на все окно
    tg.MainButton.text = "Коммерческое предложение"; //изменяем текст кнопки 
    tg.MainButton.textColor = "#fff"; //изменяем цвет текста кнопки
    tg.MainButton.color = "#e01818"; //изменяем цвет бэкграунда кнопки
    tg.MainButton.onClick(function() {document.getElementById(`blurBlock_${idPhoto.split('_')[1]}`).style.display == 'flex' ?closeWindow(idPhoto):GetKP()})
    tg.MainButton.show() 
    href = window.location.href

    ID_USER =  new URL(href).searchParams.get('tg_id')
    UserName = new URL(href).searchParams.get('username')

    new URL(href).searchParams.get('keyCP')!= null? ( key = new URL(href).searchParams.get('keyCP'), getKP_info()) : writeNewCP('Separator')


    getProvider_listSorter()
    // document.getElementById('mainBlock').style.filter = 'none'
}

function openGridPosition(id){
    var ID_M = id.split('_')[1]
    document.getElementById(`listGridPosition_${ID_M}`).style.display = 'flex'
    document.getElementById(`gridPosition_${ID_M}`).style.display = 'none'
}
function CloseGridPosition(id){
    var ID_M = id.split('_')[1]
    document.getElementById(`listGridPosition_${ID_M}`).style.display = 'none'
    document.getElementById(`gridPosition_${ID_M}`).style.display = 'flex'
} 
function openprocessing(id){
    var ID_M = id.split('_')[1]
    document.getElementById(`listProcessing_${ID_M}`).style.display = 'flex'
    document.getElementById(`processing_${ID_M}`).style.display = 'none'
}
function Closeprocessing(id){
    var ID_M = id.split('_')[1]
    document.getElementById(`listProcessing_${ID_M}`).style.display = 'none'
    document.getElementById(`processing_${ID_M}`).style.display = 'flex'
} 
var ClassMAshine = {
    'МУЗ 8':{
        '0':1,
        '1':3,
        '2':3
    },
    'МУЗ 16':{
        '0':2,
        '1':6,
        '2':6
    }
}

var TypeClear = {
    'Предварительная': 'ПРЕДВАРИТЕЛЬНАЯ ОЧИСТКА',
    'Продовольственная': 'ПРОДОВОЛЬСТВЕННАЯ ОЧИСТКА',
    'Вторичная': 'ВТОРИЧНАЯ (СЕМЕННАЯ) ОЧИСТКА'
}
var Blockline = {
    0:'А',
    1:'Б',
    2:'В'
}
var Price_KP
var ArrSelect = []
var Ids_ListSieve = []
var list_Product = []
var IndexList = []
var ListMachine = []
var List_Provider = []
var All_ListMachine, All_list_Product, All_IndexList, All_Ids_ListSieve, All_sieve_size, All_pneumatic_feed

function getProvider_listSorter(){
    List = 'provider_list'

    $.ajax({
        url: `/off_bot/API/getProviderData`,
        type: 'get',
        success: function (data) {
          List_Provider = data['provider']
          selectProvider()
            
          },
        error: function (error) {
            console.log('error', error);
        }
    });
}


function getProd_listSorter(){
    List = 'calc_sieve'

    $.ajax({
        url: `/off_bot/API/getListData/${lang}`,
        type: 'get',
        success: function (data) {
            
          All_list_Product = data['prod']
          All_IndexList = data['index']
          All_Ids_ListSieve = data['ids']
          All_ListMachine = data['machine']
          All_sieve_size = data['sieve_size']
          All_pneumatic_feed = data['Pneumatic_feed']
          Choice_Provider()
            
          },
        error: function (error) {
            console.log('error', error);
        }
    });
}

function selectProvider(){
    let Parent = document.getElementById('provider_equipment')
    let Child = Parent.children[0]

    for (var i = 0; i <= List_Provider.length-1; i++){
        console.log(List_Provider[i].id)
        var Clone = Child.cloneNode(true)
        Clone.value = List_Provider[i].id
        Clone.innerText = List_Provider[i].organization_shortname
        Clone.disabled = false
        Parent.appendChild(Clone)
    }
    document.getElementById('provider_equipment').value = 1    

    getProd_listSorter()
}
function Choice_Provider() {
    id_provider = Number(document.getElementById('provider_equipment').value)

    ListMachine = All_ListMachine.filter(function(f) { return f['id_provider'] == id_provider});
    IndexList = All_IndexList.filter(function(f) { return f['id_provider'] == id_provider});
    // list_Product = All_list_Product.filter(function(f) { return f['id_provider'] == id_provider}); 
    list_Product = All_list_Product
    Ids_ListSieve = All_Ids_ListSieve.filter(function(f) { return f['id_provider'] == id_provider});

    
    let Parent = document.getElementById('ParentList')
    for (var n = Parent.children.length-1; n >= 1; n--) {
        Parent.children[n].remove()
    }

    FirstBlock()
}

function FirstBlock(){
    mainBlock.style.display = 'flex'
    addNewBlock()
    document.getElementById('productAdd_1').value = 'Пшеница'
    ChoiceProd(`productAdd_${'1'}`)
    CloseInfoSorter()
}
function AddNewProd(id){
    openprocessing(`listProcessing_${id}`)
    // ClickCheckBoxType(`CheckBox_0_${id}`)
    ClickCheckBoxType(`CheckBox_1_${id}`)
    // ClickCheckBoxType(`CheckBox_2_${id}`)
    Closeprocessing(`CloseClearList_${id}`)
    openGridPosition(`gridPosition_${id}`)
    ClickCheckBoxletter(`CheckBoxType_0_${id}`)
    ClickCheckBoxletter(`CheckBoxType_1_${id}`)
    ClickCheckBoxletter(`CheckBoxType_2_${id}`)
    CloseGridPosition(`CloseTypeList_${id}`)

}
function ScroolProd(id){
    var Prod = []
    let Parent = document.getElementById(id)
    for (var n = Parent.children.length-1; n >= 1; n--) {
        Parent.children[n].remove()
    }
    let Children = Parent.children[0]
    Object.keys(list_Product).map(item=>{
        if (Prod.includes(list_Product[item].Prod) == false){
            var Clone = Children.cloneNode(true)
            Clone.innerText = list_Product[item].Prod
            Clone.value = list_Product[item].Prod
            Parent.appendChild(Clone)
            Prod.push(list_Product[item].Prod)
        }
    })
}
function ChoiceProd(id){
    var ID_M = id.split('_')[1]
    ArrSelect = list_Product.filter(function(f) { return f['Prod'] == document.getElementById(`productAdd_${ID_M}`).value});
    if(document.getElementById(`productAdd_${ID_M}`).value == '0'){
        document.getElementById(`blockChoice_${ID_M}`).style.filter = 'blur(2px)'
        document.getElementById(`blockChoice_${ID_M}`).style.pointerEvents = 'none'
    }
    else{
        document.getElementById(`blockChoice_${ID_M}`).style.filter = 'none'
        document.getElementById(`blockChoice_${ID_M}`).style.pointerEvents = 'auto'
    }
    rebuild(id)
    if(!document.getElementById(`CheckBox_0_${ID_M}`).children[0].checked && !document.getElementById(`CheckBox_1_${ID_M}`).children[0].checked && !document.getElementById(`CheckBox_2_${ID_M}`).children[0].checked){
        AddNewProd(ID_M)
    }
}
function addNewBlock(){
    let Parent = document.getElementById('ParentList')
    NewID = Number(Parent.children[Parent.children.length-1].id.split('_')[1] )+ 1
    let Children = Parent.children[0]
    var Clone = Children.cloneNode(true)
    Clone.style.display = 'flex'
    Clone.id = `windowProduct_${NewID}`
    Clone.children[0].id = `blurBlock_${NewID}`
    Clone.children[0].children[0].children[0].children[0].children[0].id = `swiper1_${NewID}`
    // Clone.children[0].children[0].children[0].children[0].children[1].id = `swiper2_${NewID}`
    Clone.children[0].children[0].children[1].children[0].id = `buttonChange_${NewID}`
    Clone.children[1].children[0].children[1].id = `productAdd_${NewID}`
    Clone.children[1].children[0].children[2].id = `DeleteCard_${NewID}`
    Clone.children[1].children[1].id = `blockChoice_${NewID}`
    Clone.children[1].children[1].children[0].children[0].id = `typeMachine_${NewID}`
    for(item in ListMachine){
        var clone2 =  Clone.children[1].children[1].children[0].children[0].children[0].cloneNode(true)
        clone2.style.display = 'flex'
        clone2.innerText = ListMachine[item]['name']
        clone2.value = ListMachine[item]['name']

        Clone.children[1].children[1].children[0].children[0].appendChild(clone2)
        item == 0? Clone.children[1].children[1].children[0].children[0].value = ListMachine[item]['name']:0
    }

    Clone.children[1].children[1].children[0].children[1].children[0].id = `processing_${NewID}`
    Clone.children[1].children[1].children[0].children[1].children[1].id = `listProcessing_${NewID}`
    Clone.children[1].children[1].children[0].children[1].children[1].children[0].id = `CheckBox_0_${NewID}`
    Clone.children[1].children[1].children[0].children[1].children[1].children[1].id = `CheckBox_1_${NewID}`
    Clone.children[1].children[1].children[0].children[1].children[1].children[2].id = `CheckBox_2_${NewID}`
    Clone.children[1].children[1].children[0].children[1].children[1].children[3].id = `CloseClearList_${NewID}`
    Clone.children[1].children[1].children[0].children[2].children[0].id = `gridPosition_${NewID}`
    Clone.children[1].children[1].children[0].children[2].children[1].id = `listGridPosition_${NewID}`
    Clone.children[1].children[1].children[0].children[2].children[1].children[0].id = `CheckBoxType_0_${NewID}`
    Clone.children[1].children[1].children[0].children[2].children[1].children[1].id = `CheckBoxType_1_${NewID}`
    Clone.children[1].children[1].children[0].children[2].children[1].children[2].id = `CheckBoxType_2_${NewID}`
    Clone.children[1].children[1].children[0].children[2].children[1].children[3].id = `CloseTypeList_${NewID}`
    Clone.children[1].children[1].children[1].id = `blockPhoto_${NewID}`
    
    Clone.children[1].children[1].children[1].children[0].id = `stubPhoto_${NewID}`

    Clone.children[1].children[1].children[1].children[0].children[0].id = `photoIcon_${NewID}`
    Clone.children[1].children[1].children[1].children[0].children[1].id = `fileElem_${NewID}`
    Clone.children[1].children[1].children[1].children[1].id = `SliderPhoto_${NewID}`

    Clone.children[1].children[1].children[1].children[1].addEventListener('keydown', (event) => {event.preventDefault();});
    Clone.children[1].children[1].children[1].children[1].children[1].children[0].id = `openPhoto_${NewID}`
    Clone.children[1].children[2].id = `ToglMachine_${NewID}`
    Clone.children[1].children[2].children[1].children[0].id = `Label_${NewID}`

    Clone.children[1].children[3].id = `blockCleaning_${NewID}`



    Parent.appendChild(Clone)
    Clone.scrollIntoView({ block: "center", behavior: "smooth" });
    ScroolProd( `productAdd_${NewID}`)
    document.getElementById(`blockChoice_${NewID}`).style.filter = 'blur(2px)'
    document.getElementById(`blockChoice_${NewID}`).style.pointerEvents = 'none'
}
function ClickCheckBoxType(id){
    document.getElementById(id).children[0].checked? deleteBlockLine(id): (AddBlockLine(id))
    document.getElementById(id).children[0].checked = !document.getElementById(id).children[0].checked

}
function AddBlockLine(id){
    var ID_M = id.split('_')[2]
    document.getElementById(`blockCleaning_${ID_M}`).children[Number(id.split('_')[1])].innerHTML!=''? document.getElementById(`blockCleaning_${ID_M}`).children[Number(id.split('_')[1])].children[0].remove():0
    let Parent  =  document.getElementById(`blockCleaning_${ID_M}`).children[Number(id.split('_')[1])]
    let Child  = document.getElementById(`blockCleaning_${ID_M}`).children[3]
    var Clone = Child.cloneNode(true)
    Clone.style.display = 'flex'
    Clone.id =`Blockline_${id.split('_')[1]}_${ID_M}`
    Clone.children[2].id =`blockResultCleaning_${id.split('_')[1]}_${ID_M}`
    Clone.children[2].children[0].id =`blockResultCleaningText_${id.split('_')[1]}_${ID_M}`

    Clone.children[0].children[0].innerText = `${document.getElementById(id).children[1].innerText} очистка`
    for (var n = Clone.children[1].children.length; n > 0; n--){
        Clone.children[1].children[n]!= undefined? Clone.children[1].children[n].remove():0
    }
    Parent.appendChild(Clone)

    for (var i = 0; i < 3; i++){
        if (document.getElementById( `listGridPosition_${ID_M}`).children[i].children[0].checked == false){continue}
        AddLine(`CheckBoxType_${i}_${ID_M}`)
    }

    
}
function ClickCheckBoxletter(id){
    !document.getElementById(id).children[0].checked && document.getElementById(id).children[0].disabled == false ? ( document.getElementById(id).children[0].checked =true, AddLine(id)) : document.getElementById(id).children[0].checked = false, deleteLine(id)
    
    ToglCheckAnalys == true ?ResultAnalys(id.split('_')[2], List_result_analys_sieve):0
}
function AddLine(id){
    var ID_M = id.split('_')[2]
    for (var i = 0; i < 3; i++){
        if (document.getElementById(`Blockline_${i}_${ID_M}`)!= null){
            for (var n = document.getElementById(`Blockline_${i}_${ID_M}`).children[1].children.length; n > 0; n--){
                document.getElementById(`Blockline_${i}_${ID_M}`).children[1].children[n]!= undefined? document.getElementById(`Blockline_${i}_${ID_M}`).children[1].children[n].remove():0
            }
        }
    }
    for (var n = 0; n < 3; n++){
        if (document.getElementById(`Blockline_${n}_${ID_M}`)== null ){continue}
        for (var i = 0; i < document.getElementById(`listGridPosition_${ID_M}`).children.length -1; i++){
            if (document.getElementById(`listGridPosition_${ID_M}`).children[i].children[0].checked == false){continue}
            newSelect = ArrSelect.filter(function(f) { return f['type_letter'] == Blockline[i]});
            newSelect = newSelect.filter(function(f) { return f['type_clear'] == TypeClear[document.getElementById(`Blockline_${n}_${ID_M}`).children[0].children[0].innerText.split(' ')[0]]});
            formSieve = newSelect[0]['form']
            sieve_size = ListMachine.filter(function(f) { return f['name'] == document.getElementById(`typeMachine_${ID_M}`).value})[0]['sieve_size'];
            newCount = Ids_ListSieve.filter(function(f) { return f['Type'] == formSieve && f['sieve_size'] == sieve_size}).sort((a, b) => a.Count - b.Count);
            let Parent_2  =  document.getElementById(`Blockline_${n}_${ID_M}`).children[1]
            let Child_2  = Parent_2.children[0]
            var Clone_2 = Child_2.cloneNode(true)
            Clone_2.id = `lineOne_${i}_${ID_M}_${n}`
            Clone_2.style.display = 'flex'
            Clone_2.children[0].children[0].innerText = Blockline[i]
            Clone_2.children[0].children[1].id = `choice_${i}_${ID_M}_${n}`
            Clone_2.children[0].children[1].checked = true
            Clone_2.children[0].children[2].id = `typeletter_${n}_${i}_${ID_M}_0`
            Clone_2.children[0].children[2].value = formSieve
            Clone_2.children[0].children[3].id = `numberletter_${n}_${i}_${ID_M}_0`
            Clone_2.children[0].children[4].id = `resultcleaning_${n}_${i}_${ID_M}_0`

            Parent_2.appendChild(Clone_2)
            
            selectParent = document.getElementById(`numberletter_${n}_${i}_${ID_M}_0`)
            selectChildren = selectParent.children[0]
            if (newSelect.length!= 0){
                min = Number(newSelect[0]['min'])
                max = Number(newSelect[0]['max'])
            }
            for (var q = 0; q < newCount.length; q++){
                var selectClone = selectChildren.cloneNode(true)
                selectClone.style.display = 'flex'
                var count = Number(newCount[q]['Count']).toFixed(1)
                selectClone.innerText = count
                selectClone.value = count
                if (newSelect.length!= 0){
                    count<=max && count>= min? selectClone.style.backgroundColor = '#92cbee':0
                }
                selectParent.appendChild(selectClone)
                if (newSelect.length!= 0){
                    count == max? document.getElementById(`numberletter_${n}_${i}_${ID_M}_0`).value = count:0
                }
            }
        }
    }

    ToglCheckAnalys == true ?ResultAnalys(ID_M, List_result_analys_sieve):GetItog(id)
}
function deleteLine(id){
    for (var i = 0; i < 3; i++){
        if (document.getElementById(`Blockline_${i}`)!= null){
            for (var n = document.getElementById(`Blockline_${i}`).children[1].children.length; n > 0; n--){
                document.getElementById(`Blockline_${i}`).children[1].children[n]!= undefined? document.getElementById(`Blockline_${i}`).children[1].children[n].remove():0
            }
        }
    }
    AddLine(id)
}
function deleteBlockLine(id){
    var ID_M = id.split('_')[2]
    if( document.getElementById(`blockCleaning_${ID_M}`).children[Number(id.split('_')[1])].children[0] != undefined){
        document.getElementById(`blockCleaning_${ID_M}`).children[Number(id.split('_')[1])].children[0].remove()
    }
    GetItog(id)
}
function ClickChangeSieves(id){
    document.getElementById(id).checked? (deleteChangeSieves(id)):( ChangeSieves(id))
}
function ChangeSieves(id){
    var ID_P = id.split('_')[1]
    var ID_M = id.split('_')[2]
    var ID_G = id.split('_')[3]

    Parent = document.getElementById(`lineOne_${ID_P}_${ID_M}_${ID_G}`)
    Child = Parent.children[0]
    choicemachine = document.getElementById(`typeMachine_${ID_M}`).value

    
    maxI = ListMachine.filter(function(f) { return f['name'] == choicemachine})[0]['sieve_position'][ID_P]-1

    // maxI = ClassMAshine[choicemachine][ID_P]-1
    for (var i = 0; i < maxI; i++){
        Clone = Child.cloneNode(true)
        Clone.id = ''
        Clone.children[2].id = `typeletter_${i+1}_${ID_P}_${ID_M}_${ID_G}`
        Clone.children[3].id = `numberletter_${i+1}_${ID_P}_${ID_M}_${ID_G}`
        Clone.children[0].innerText = '-'
        var  div = document.createElement('div')
        div.style.width = '19px'
        Clone.children[1].outerHTML = div.outerHTML
        Parent.appendChild(Clone)
    }
}
function deleteChangeSieves(id){
    var ID_P = id.split('_')[1]
    var ID_M = id.split('_')[2]
    var ID_G = id.split('_')[3]
    var ID_K = id.split('_')[3]

    Parent = document.getElementById(`lineOne_${ID_P}_${ID_M}_${ID_G}`)
    for (var i = Parent.children.length-1; i > 0; i--){
        Parent.children[i].remove()
    }
}
async function rebuild(id){
    var ID_M = id.split('_')[1]
    CheckParent = document.getElementById(`listProcessing_${ID_M}`)
    Machine = ListMachine.filter(function(f) { return f['name'] == document.getElementById(`typeMachine_${ID_M}`).value})[0]['sieve_position']
    for (var i = 0; i < 3; i++){

        // CheckParent.children[i].children[0].checked? (CheckParent.children[i].click()):0
        
        if(CheckParent.children[i].children[0].checked){
            document.getElementById(`CheckBoxType_${i}_${ID_M}`).children[0].disabled = false
            CheckParent.children[i].click()
            CheckParent.children[i].click()
            if(Machine[i]==0 ){
                document.getElementById(`CheckBoxType_${i}_${ID_M}`).children[0].checked ? (document.getElementById(`CheckBoxType_${i}_${ID_M}`).click(), document.getElementById(`CheckBoxType_${i}_${ID_M}`).children[0].disabled = true):0
            }
            else{
                !document.getElementById(`CheckBoxType_${i}_${ID_M}`).children[0].checked ? (document.getElementById(`CheckBoxType_${i}_${ID_M}`).click()):0
            }
            
            
        }
    }
  

}


function DeteleCart(id){
    var ID_M = id.split('_')[1]
    document.getElementById(`windowProduct_${ID_M}`).remove()
    GetItog(id)
}
var result = {}


function ChoiseTypeSieve(id){

    var ID_P = id.split('_')[1]
    var ID_M = id.split('_')[2]
    var ID_G = id.split('_')[3]
    var ID_K = id.split('_')[4]
    console.log(`Blockline_${ID_K}_${ID_G}`)

    formSieve = document.getElementById(id).value
    sieve_size = ListMachine.filter(function(f) { return f['name'] == document.getElementById(`typeMachine_${ID_G}`).value})[0]['sieve_size'];
    newCount = Ids_ListSieve.filter(function(f) { return f['Type'] == formSieve && f['sieve_size'] == sieve_size}).sort((a, b) => a.Count - b.Count);
    selectParent = document.getElementById(`numberletter_${ID_P}_${ID_M}_${ID_G}_${ID_K}`)
    for (var i = selectParent.children.length-1; i > 0; i--){
        selectParent.children[i].remove()
    }
    selectChildren = selectParent.children[0]
    for (var q = 0; q < newCount.length; q++){
        var selectClone = selectChildren.cloneNode(true)
        selectClone.style.display = 'flex'
        var count = Number(newCount[q]['Count']).toFixed(1)
        selectClone.innerText = count
        selectClone.value = count
        if (newSelect.length!= 0){
            count<=max && count>= min? selectClone.style.backgroundColor = '#92cbee':0
        }
        selectParent.appendChild(selectClone)
        if (newSelect.length!= 0){
            // count == max?  Clone_2.children[0].children[3].value = count:0
        }
    }

    GetItog(id)
}


function GetItog(id){
    var price = 0

    result = {}
    ParentList
  

    testArr = {}
    for (var q = 1; q < document.getElementById('ParentList').children.length; q++){
        ID_M = document.getElementById('ParentList').children[q].id.split('_')[1]
        Parent = document.getElementById(`blockCleaning_${ID_M}`)
        Machine = ListMachine.filter(function(f) { return f['name'] == document.getElementById(`typeMachine_${ID_M}`).value})[0]['sieve_position']

        PriceMachine = ListMachine.filter(function(f) { return f['name'] == document.getElementById(`typeMachine_${ID_M}`).value})[0]['price']
        document.getElementById(`Label_${ID_M}`).checked ? price += Number(PriceMachine) : 0
        for (var i = 0; i < Parent.children.length; i++){
            if(Parent.children[i].innerHTML ==''){continue}
            ChildParent = Parent.children[i].children[0].children[1]
            if(ChildParent ==undefined){continue}
            for (var n = 1; n < ChildParent.children.length; n++){
                for (var k = 0; k < ChildParent.children[n].children.length; k++){
                    if(ChildParent.children[n].children[k].children[2].value =='-'){continue}
                    if(ChildParent.children[n].children[k].children[3].value =='-'){continue}
                    count = 1* Machine[ChildParent.children[n].children[k].children[1].id.split('_')[1]]
                    type_letter = ChildParent.children[n].children[k].children[0].innerText
                    testPAR = `${Parent.children[i].children[0].children[0].children[0].innerHTML}|${ChildParent.children[n].children[k].children[2].value}`
                    testArr[`${String(ChildParent.children[n].children[k].children[3].value)}|${count}|${type_letter}`] == undefined ?( testArr[`${String(ChildParent.children[n].children[k].children[3].value)}|${count}|${type_letter}`] = {}):0
                    testArr[`${String(ChildParent.children[n].children[k].children[3].value)}|${count}|${type_letter}`]= testPAR
                    
                }
            }
        }
    }
    var text = ''
    console.log(testArr)
    for(var i = 0; i< Object.keys(testArr).length; i++){
        key_res = Object.keys(testArr)[i]
        size = key_res.split('|')[0]
        count = Number(key_res.split('|')[1])
        sieveEl= testArr[key_res].split('|')[1]
        result[sieveEl] == undefined ? result[sieveEl] = {}:0
        result[sieveEl][size]==undefined ? result[sieveEl][size] =  count :result[sieveEl][size] +=  count
    }

    for(var i = 0; i< Object.keys(result).length; i++){
        text+= `Решето ${Object.keys(result)[i]}:`
        if(result[Object.keys(result)[i]] ==undefined){continue}
        for(var n = 0; n< Object.keys(result[Object.keys(result)[i]]).length; n++){
            sieveEl =  Object.keys(result[Object.keys(result)[i]])[n]
            count = Number(result[Object.keys(result)[i]][sieveEl])
            text += `<p>${sieveEl}: ${count} шт.</p>`
            sieve_size = ListMachine.filter(function(f) { return f['name'] == document.getElementById(`typeMachine_${ID_M}`).value})[0]['sieve_size'];

            price_id = Ids_ListSieve.filter(function(f) { return f['Count'] == Number(sieveEl) && f['Type'] == Object.keys(result)[i] && f['sieve_size'] == sieve_size })[0]['price']
            console.log(price_id, count)
            price += price_id * count
            // price +=  Number(sieveEl)< 1.1 ? 21600 *count : 10800 *count
        }
    }
    Price_KP = price
    document.getElementById(`resultSievePrice`).innerText = `Итого - ${price.toLocaleString()} рублей`
    document.getElementById(`resultSieve`).innerHTML = text
    ToglCheckAnalys == true ? Start_calculate(ID_M, List_result_analys_sieve) :0
}
testArr = {}

var number_A, number_B,number_C, Index, firstPhoto
var List_result_analys, List_result_analys_sieve
var ToglCheckAnalys = false

async function CheckAnalys(key, ID_M, toglLoop){
    console.log(key)
    toglLoop == true ?await sleep(5000):await sleep(2000)
    $.ajax({
        type: 'GET',
        url: `/off_bot/API/Sieve_GetData/${key}`,
        processData: false,
        contentType: false,
        success: function(data){
            console.log(data)
            List_result_analys = data['result'][0]
            if(List_result_analys == undefined && toglLoop == true){
                CheckAnalys(key, ID_M, true)

            }
            else{
                if(data['result'] != false){
                    List_result_analys_sieve = Object.values(List_result_analys[2])
                    processing_parameters_analys(List_result_analys_sieve, ID_M, data)
                    GoodToast('Анализ готов')
                }


                mainBlock.style.filter = 'none'
                mainBlock.style.pointerEvents = 'auto'
              

            }
        },
        error: function (error) {
            console.log('error', error);
            // add_analysis(id)
        }
    })  
}

var files_photo
function processing_parameters_analys(List_result_analys_sieve, ID_M, data){
    ToglCheckAnalys= true
    // Index = data['text']
    Parent = document.getElementById(`blockCleaning_${ID_M}`)
    document.getElementById(`productAdd_${ID_M}`).value = data['result'][0][4]
    for (var i = 0; i < Parent.children.length; i++){
        Parent = document.getElementById(`blockCleaning_${ID_M}`)
        if(Parent.children[i].innerHTML ==''){continue}
        ChildParent = Parent.children[i].children[0].children[1]
        if(ChildParent ==undefined){continue}
        for (var n = 1; n < ChildParent.children.length; n++){
            newSelect = ArrSelect.filter(function(f) { return f['type_letter'] == Blockline[n-1]});
            newSelect = newSelect.filter(function(f) { return f['type_clear'] == TypeClear[Parent.children[i].children[0].children[0].innerText.split(' ')[0]]});
            formSieve = newSelect[0]['form']
            document.getElementById(ChildParent.children[n].children[0].children[2].id).value = formSieve
            sieve_size = ListMachine.filter(function(f) { return f['name'] == document.getElementById(`typeMachine_${ID_M}`).value})[0]['sieve_size'];
            newCount = Ids_ListSieve.filter(function(f) { return f['Type'] == formSieve && f['sieve_size'] == sieve_size}).sort((a, b) => a.Count - b.Count);
            selectParent = document.getElementById(ChildParent.children[n].children[0].children[3].id)
            for (var w = selectParent.children.length-1; w > 0; w--){
                selectParent.children[w].remove()
            }
            selectChildren = selectParent.children[0]
            for (var q = 0; q < newCount.length; q++){
                var selectClone = selectChildren.cloneNode(true)
                selectClone.style.display = 'flex'
                var count = Number(newCount[q]['Count']).toFixed(1)
                selectClone.innerText = count
                selectClone.value = count
                if (newSelect.length!= 0){
                    count<=max && count>= min? selectClone.style.backgroundColor = '#92cbee':0
                }
                selectParent.appendChild(selectClone)
            }
        }
    }

    
    


    files_photo =data['result'][0][3]
    addPhoto(ID_M, List_result_analys_sieve)
}


function addPhoto(ID_M, List_result_analys_sieve){
    document.getElementById(`SliderPhoto_${ID_M}`).innerHTML = document.getElementById(`SliderPhoto`).innerHTML
    var Parent  = document.getElementById(`SliderPhoto_${ID_M}`).children[0]
    var Children = Parent.children[0]
    for(var i = 0; i < files_photo; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        Clone.style.width = '80%'
        Clone.style.height = '100%'
        Clone.style.backgroundImage = `url(/off_bot/static/img_sieve/${key}/${key}_photo_${i}.png)`
        Parent.appendChild(Clone)
    }
    document.getElementById(`SliderPhoto_${ID_M}`).getElementsByClassName('openPhoto')[0].id = `openPhoto_${ID_M}`
    ResultAnalys(ID_M, List_result_analys_sieve)
}
function ResultAnalys(ID_M, List_result_analys){
    allheight = []
    allwidth = []
    for (var i = 0; i < List_result_analys.length - 1; i++){
        allheight.push(Number(List_result_analys[i]['h']))
        allwidth.push(Number(List_result_analys[i]['w']))
    }
    number_A = Math.max(...allheight)
    number_B = median(allwidth)
    toglSieve = true
    Parent = document.getElementById(`blockCleaning_${ID_M}`)

    for (var i = 0; i < Parent.children.length; i++){
        Machine = ClassMAshine[document.getElementById(`typeMachine_${ID_M}`).value]
        if(Parent.children[i].innerHTML ==''){continue}
        conf_prod = IndexList.filter(function(f) { return f['prod'] == document.getElementById(`productAdd_${ID_M}`).value})[0]['Count']
        ChildParent = Parent.children[i].children[0].children[1]
        if(ChildParent ==undefined){continue}
        for (var n = 1; n < ChildParent.children.length; n++){
            alloptions = []
            for (var  q= 1; q < ChildParent.children[n].children[0].children[3].children.length; q++){
                alloptions.push(Number(Number(ChildParent.children[n].children[0].children[3].children[q].value).toFixed(1)))
            }

            Step = med_Step(alloptions)
            ChildParent.children[n].id.split('_')[1] == 0? ChildParent.children[n].children[0].children[3].value = Number(closest(alloptions, (number_A*1.5))).toFixed(1) :0
            if(ChildParent.children[n].children[0].children[2].value == 'Прямоугольное'){
                ChildParent.children[n].id.split('_')[1] == 1?ChildParent.children[n].children[0].children[3].value = closest(alloptions, (closest(alloptions, number_B** conf_prod) + Number(Step))).toFixed(1):0
                ChildParent.children[n].id.split('_')[1] == 2?ChildParent.children[n].children[0].children[3].value = closest(alloptions, (closest(alloptions, number_B** conf_prod) - Number(Step))).toFixed(1):0
            }
            else{
                conf_prod = IndexList.filter(function(f) { return f['prod'] == document.getElementById(`productAdd_${ID_M}`).value})[0]['Count']
                ChildParent.children[n].id.split('_')[1] == 1?ChildParent.children[n].children[0].children[3].value = closest(alloptions, (closest(alloptions, number_B) + Number(Step))).toFixed(1):0
                ChildParent.children[n].id.split('_')[1] == 2?ChildParent.children[n].children[0].children[3].value = closest(alloptions, (closest(alloptions, number_B) - Number(Step))).toFixed(1):0
            }

        }
        
    }
    GetItog('')

}
function med_Step(array){
    let totalStep = 0;
    for (let i = 1; i < array.length; i++) {
        totalStep += Math.abs(array[i] - array[i - 1]);
    }
    averageStep = Number((totalStep / (array.length - 1)).toFixed(1))
    return averageStep
}
function closest(arr, target) {
    return arr.reduce((prev, curr) =>
      Math.abs(curr - target) < Math.abs(prev - target) ? curr : prev
    );
  }
function median(arr) {
    arr.sort((a, b) => a - b);
    let midIdx = Math.floor(arr.length / 2);
  
    return arr.length % 2 !== 0 ? arr[midIdx] : (arr[midIdx - 1] + arr[midIdx]) / 2;
}

function images_load(id){
    var ID_M = id.split('_')[1]

    document.getElementById("fileElem_"+String(ID_M)).value = ''
    var el = document.getElementById("fileElem_"+String(ID_M));
    if (el) {
      el.click();
    }
}

var len_Befor, len_After
var rectPassedResult
function Start_calculate(id, List_result_analys_sieve){
    conf_prod = IndexList.filter(function(f) { return f['prod'] == document.getElementById(`productAdd_${id}`).value})[0]['Count']
    Block_cleaning = document.getElementById(`blockCleaning_${id}`)
    for(var i = 0; i< Block_cleaning.children.length-1; i++){
        let clone_List_result_analys = List_result_analys_sieve


        if(Block_cleaning.children[i].children.length ==0){continue}

        Parent_block = Block_cleaning.children[i].children[0].children[1]
        text = ''
        togl_full = false
        for(var n = 1; n< Parent_block.children.length; n++){
            clone_List_result_analys_res = []
            size =  Parent_block.children[n].children[0].children[3].value
            sieveEl=  Parent_block.children[n].children[0].children[2].value
            type_letter = Parent_block.children[n].children[0].children[0].innerText
            el_sieve =  All_Ids_ListSieve.filter(function(f) { return f['id_provider'] == id_provider &&  f['Type'] == sieveEl &&  f['Count'] == size})[0]

            width = Number(el_sieve['Count'])
            var cleaning_List_result_analys = []
            remainingGrains = []
            switch (sieveEl){
                case 'Прямоугольное':
                    length = Number(el_sieve['length'])
                    togl = true
                    rectPassedResult = calculateRectangularSieve(clone_List_result_analys, width, length, togl, conf_prod);
                    remainingGrains = rectPassedResult.remainingGrains
                    Left_percent = rectPassedResult.percent
                    clone_List_result_analys = rectPassedResult.passedGrains
                break
                case 'Шестигранное':
                    length = Number(el_sieve['length'])
                    togl = true
                    rectPassedResult = calculateHexagonalSieve(clone_List_result_analys, width, togl, conf_prod);
                    remainingGrains = rectPassedResult.remainingGrains
                    Left_percent = rectPassedResult.percent
                    clone_List_result_analys = rectPassedResult.passedGrains                    
                break
                case 'Треугольное':
                    length = Number(el_sieve['length'])
                    togl = true
                    rectPassedResult = calculateEquilateralTriangleSieve(clone_List_result_analys, width, togl, conf_prod);
                    remainingGrains = rectPassedResult.remainingGrains
                    Left_percent = rectPassedResult.percent
                    clone_List_result_analys = rectPassedResult.passedGrains
                break
                case 'Круглое':

                    length = Number(el_sieve['length'])
                    togl = true
                    rectPassedResult = calculateCircularSieve(clone_List_result_analys, width, togl);
                    remainingGrains = rectPassedResult.remainingGrains
                    Left_percent = rectPassedResult.percent
                    clone_List_result_analys = rectPassedResult.passedGrains
                break
            }

            console.log(type_letter, clone_List_result_analys.length)

            
            togl_full == true ?Parent_block.children[n].children[0].children[4].style.display = 'none' : Parent_block.children[n].children[0].children[4].style.display = 'flex'
            Parent_block.children[n].children[0].children[4].children[0].innerText = `${Left_percent}%`
            if(Left_percent == 100){togl_full = true}

        }
        // percent = (( clone_List_result_analys.length / List_result_analys_sieve.length) * 100).toFixed(1)
        text=`Доля очищенного зерна: ${Left_percent}%`
        document.getElementById(`blockResultCleaning_${i}_${id}`).style.display = 'flex'
        document.getElementById(`blockResultCleaningText_${i}_${id}`).innerText = text
    }
}

// Прямоугольное решето
function calculateSieveByPredicate(grainData, returnPassed, predicate) {
    const filteredGrains = grainData.filter(function(grain) {
        return returnPassed ? predicate(grain) : !predicate(grain);
    });
    const remainingGrains = grainData.filter(function(grain) {
        return !filteredGrains.includes(grain);
    });
    const percent = (remainingGrains.length / (List_result_analys_sieve.length)) * 100;

    return {
        grains: filteredGrains.length,
        percent: percent.toFixed(1),
        passedGrains: filteredGrains,
        notPassedGrains: remainingGrains,
        updatedGrainData: remainingGrains
    };
}

function calculateRectangularSieve(grainData, sieveWidth, sieveLength, returnPassed,conf_prod) {
    return calculateSieveByPredicate(grainData, returnPassed, function(grain) {
        return Number(grain.w) <= sieveWidth && Number(grain.h) <= sieveLength;
    });
}



// Шестигранное решето
function calculateHexagonalSieve(grainData, inscribedDiameter, returnPassed, conf_prod) {
    const sideLength = 2 * (inscribedDiameter / Math.sqrt(3));
    const height = inscribedDiameter;

    return calculateSieveByPredicate(grainData, returnPassed, function(grain) {
        return Number(grain.w) <= sideLength && Number(grain.w) * conf_prod <= height;
    });
}

// Правильное треугольное решето
function calculateEquilateralTriangleSieve(grainData, sideLength, returnPassed,conf_prod) {
    const triangleHeight = Math.sqrt(3) / 2 * sideLength;

    return calculateSieveByPredicate(grainData, returnPassed, function(grain) {
        return Number(grain.w) <= sideLength && Number(grain.w) * conf_prod <= triangleHeight;
    });
}

// Круглое решето
function calculateCircularSieve(grainData, sieveDiameter, returnPassed ) {
    return calculateSieveByPredicate(grainData, returnPassed, function(grain) {
        return Number(grain.w) <= sieveDiameter;
    });
}



function handleFiles_sieve(files_photo, id) {
    var ID_M = id.split('_')[1]
    var urlObject = window.URL || window.webkitURL;    
    var blobLink = ''
    var files_photo = document.getElementById(`fileElem_${ID_M}`).files
    document.getElementById(`SliderPhoto_${ID_M}`).style.display = 'flex'
    document.getElementById(`stubPhoto_${ID_M}`).style.display = 'none'

    
    var Parent  = document.getElementById(`SliderPhoto_${ID_M}`).children[0]
    var Children = Parent.children[0]
    for(var i = 0; i< files_photo.length; i++){
        var Clone = Children.cloneNode(true)
        Clone.style.display = 'flex'
        blobLink = urlObject.createObjectURL(files_photo[i])
        Clone.style.width = '80%'
        Clone.style.height = '100%'
        Clone.style.backgroundImage = String("url('"+blobLink+"')")
        Parent.appendChild(Clone)
    }
    add_analysis(id)
}

async function add_analysis(id){
    var ID_M = id.split('_')[1]
    var files_photo =  document.getElementById(`fileElem_${ID_M}`).files
    product = document.getElementById(`productAdd_${ID_M}`).value
    TypeForm = new FormData();
    TypeForm.append(`file`, files_photo[0], ID_USER)

    TypeForm.append(`product`, product);

    var photoInput = document.getElementById(`SliderPhoto_${ID_M}`).children[0].children[1]
    photoInput.style.pointerEvents = 'none'
    // document.getElementById('BlockmanagerPhoto').poster = ''
    formData = TypeForm;
    $.ajax({
            type: 'POST',
            url: `/off_bot/API/Sieve_Analytics/${ID_USER}/${key}`,
            data: formData,
            processData: false,
            contentType: false,
            success: function(data){
              GoodToast('Фотография успешно загружена')
              CheckAnalys(key, ID_M, true)
            //   currentTime = Math.floor(new Date().getTime() / 1000);
            //   document.getElementById('BlockmanagerPhoto').poster =`${data}?u=currentTime`
            },
            error: function (error) {
            } 
        })  
}

machine = []
prodList = []

async function GetKP(){

    sep_machine = {}
    Sieve = {}
    photo_sorter= {}
    compressor = {}
    for (var q = 1; q < document.getElementById('ParentList').children.length; q++){
        prodList.push(document.getElementById(`productAdd_${q}`).value)
        machine = document.getElementById('ParentList').children[q].children[1].children[1].children[0].children[0].value

        if(document.getElementById(`Label_${q}`).checked == true){
            id_machine = ListMachine.filter(function(f) { return f['name'] == machine})[0]['id_row']
            Object.keys(sep_machine).includes(machine) == false ? sep_machine[id_machine] = 1 :sep_machine[id_machine] += 1
        }
        var list_type
        for (var q = 0; q < Object.keys(result).length; q++){
            type_Sieve = Object.keys(result)[q]
            
            sieve_size = ListMachine.filter(function(f) { return f['name'] == machine})[0]['sieve_size'];

            list_type = Ids_ListSieve.filter(function(f) { return f['Type'] == type_Sieve && f['sieve_size']==sieve_size})

            for (var n = 0; n < Object.keys(result[type_Sieve]).length; n++){
                size = Object.keys(result[type_Sieve])[n]
                count = result[type_Sieve][size]
                id_sieve = list_type.filter(function(f) { return f['Count'] == size})[0]['id']
                Sieve[id_sieve] = count
            }

        }

    }
    
    data_CP = {
        'cp_key': key,
        'group_info':{
            'Sieve': Sieve,
            'sep_machine': sep_machine,
            'compressor': compressor,
            'photo_sorter': photo_sorter,
            'extra_equipment':{},
            'laboratory_equipment':{},
            'Service': {},
            'attendance': {},
            'elevator' :{},
            'Pneumatic_feed':{}

        },
        'price': (Price_KP),
        'sale':0,
        'additional_info':{}
    }

    UpdateCPlist(data_CP, List_CP, pages)
   

}
var idPhoto = 'Test_0'
function expandPhoto(id){
    var ID_M = id.split('_')[1]

    document.getElementById(`blurBlock_${ID_M}`).style.display='flex'
    document.getElementById(`windowProduct_${ID_M}`).children[1].style.filter = 'blur(2px)'
    document.getElementById(`windowProduct_${ID_M}`).children[1].style.pointerEvents = 'none'
    Parent = document.getElementById(`blurBlock_${ID_M}`).children[0].children[0].children[0]
    Parent.innerHTML = document.getElementById(`blurBlock_0`).children[0].children[0].children[0].innerHTML
    ParentPhoto = document.getElementById(`SliderPhoto_${ID_M}`).children[0]
    Child = Parent.children[0]
    for (var i = 1; i < ParentPhoto.children.length; i++){
        var Clone = Child.cloneNode(true)
        Clone.style.display = 'flex'
        Clone.style.backgroundImage = ParentPhoto.children[i].style.backgroundImage
        Parent.appendChild(Clone)
    }
    tg.MainButton.textColor = "#5b6579"; //изменяем цвет текста кнопки
    tg.MainButton.color = "#f2f2f2"; //изменяем цвет бэкграунда кнопки
    tg.MainButton.text = 'Назад'
    tg.MainButton.show() 
    idPhoto = id
}
// function closePhoto(){
//     document.getElementById(`blurBlock_${ID_M}`).style.display='none'
//     document.getElementById(`windowProduct_${ID_M}`).children[1].style.filter = 'none'
//     document.getElementById(`windowProduct_${ID_M}`).children[1].style.pointerEvents = 'auto'
// }

function closeWindow(id){
    var ID_M = id.split('_')[1]
    document.getElementById(`blurBlock_${ID_M}`).style.display='none'
    document.getElementById(`windowProduct_${ID_M}`).children[1].style.filter = 'none'
    document.getElementById(`windowProduct_${ID_M}`).children[1].style.pointerEvents = 'auto'
    tg.MainButton.text = "Коммерческое предложение"
    tg.MainButton.show() 
    tg.MainButton.textColor = "#fff"; //изменяем цвет текста кнопки
    tg.MainButton.color = "#e01818";
    idPhoto = 'Test_0'
}
function InfoSorter(){
    document.getElementById('InfoBlockUser').style.display = 'flex'
    document.getElementById('mainBlock').style.filter = 'blur(2px)'
    document.getElementById('mainBlock').style.pointerEvents = 'none'
}
function CloseInfoSorter(){
    document.getElementById('InfoBlockUser').style.display = 'none'
    document.getElementById('mainBlock').style.filter = 'none'
    document.getElementById('mainBlock').style.pointerEvents = 'auto'
}

function MachineSlider(id){
    var ID_M = id.split('_')[1]
    document.getElementById(`Label_${ID_M}`).checked = !document.getElementById(`Label_${ID_M}`).checked 
    GetItog(id)

}
