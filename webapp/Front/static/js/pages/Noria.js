var tg, ID_USER,UserName, key = '', id_provider, data_CP , List_CP
var togl_check = false
pages = 'Separator'
window.onload = function() {
    tg = window.Telegram.WebApp;
    tg.disableVerticalSwipes()
    tg.expand(); //расширяем на все окно
    tg.MainButton.text = "Получить КП"; //изменяем текст кнопки 
    tg.MainButton.textColor = "#fff"; //изменяем цвет текста кнопки
    tg.MainButton.color = "#e01818"; //изменяем цвет бэкграунда кнопки
    tg.MainButton.onClick(function() {openUserInfo()})
    // tg.MainButton.offClick(function() {
    //     // document.getElementById('ListFullData').style.display == 'none' && document.getElementById('UserInfo_Block').style.display == 'none' ? openUserInfo() :0
    //     openUserInfo()
    // })
    tg.MainButton.show() 
    // tg.BackButton.hide()
    href = window.location.href
    ID_USER =  new URL(href).searchParams.get('tg_id')
    UserName = new URL(href).searchParams.get('username')

    // new URL(href).searchParams.get('keyCP')!= null? ( key = new URL(href).searchParams.get('keyCP'), getKP_info()) : writeNewCP('Separator')
    
    // key =   writeNewCP('Separator')
    
    // getProd_list()
}
var Separ_perf = [], Compressor_perf = [], List_separ=[], List_compressor= [], List_equipment=[]

function DeleteChildren(Parent){
    for (var n = Parent.children.length-1; n > 0; n--) {Parent.children[n].remove()}
}

const sliderEl = document.querySelector(".line") //ползунок
const sliderValue = document.querySelector(".value")

sliderEl.addEventListener("input", (event) => {
  const tempSliderValue = event.target.value; 
  
  sliderValue.textContent = tempSliderValue;
  
  const progress = (tempSliderValue / sliderEl.max) * 100;
 
  sliderEl.style.background = `linear-gradient(to right, rgb(134 134 134) ${progress}%, rgb(221 221 221) ${progress}%)`;
})

function increment(id) {
    let ID_M = id.split("_")[0]
    var data = Number(document.getElementById(ID_M).innerText)
    data += 1;
    document.getElementById(ID_M).innerText = data;
}
function decrement(id) {
    let ID_M = id.split("_")[0]
    var data = Number(document.getElementById(ID_M).innerText)
    if(data == 0){
        console.log(' не может быть <0')
        return
    }
    data -= 1;
    document.getElementById(ID_M).innerText = data;
}

function ChoiceNoria(value){
    console.log(value)
    var ID_M = value.split('_')[1]
    let Parent = document.getElementById('BlockCards')
    for(var i = 0; i< Parent.children.length; i++){
        Parent.children[i].id == `blockNoria${ID_M}` ? Parent.children[i].style.display = 'flex': Parent.children[i].style.display = 'none'
    }
}

function user_images_load(elementId) {
    document.getElementById('fileElem').click();  // Клик по скрытому инпуту
}

function handleFiles(files, elementId) {
    const file = files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.style.maxWidth = '100%'; // Ограничение ширины
        img.style.maxHeight = '100%'; // Ограничение высоты
        img.style.borderRadius = '10px'; 

        const container = document.getElementById('photoNoriaBlock');
        container.innerHTML = ''; // Очищаем контейнер от SVG
        container.appendChild(img); // Добавляем изображение
    }

    reader.readAsDataURL(file);
}


