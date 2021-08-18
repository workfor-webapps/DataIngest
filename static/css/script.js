
function html2json() {
  var $table = $("table")
  rows = [],
  header = [];

  $table.find("thead th").each(function () {
      header.push($(this).html());
  });
  
  //header.push("Title")
  //var pubData = $('#pub-data').data('value');
  //var title = pubData;


  $table.find("tbody tr").each(function () {
      var row = {};

      $(this).find("td").each(function (i) {
          var key = header[i],
              value = $(this).html();

          row[key] = value;
          
      });

     
      rows.push(row);
  });
  

  //construct an HTTP request
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/post_json', true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

  // send the collected data as JSON
  xhr.send(JSON.stringify(rows));

  //console.log(JSON.stringify(rows));

  // reload page
  var maxt = $('#my-data').data('value');
  var url = window.location.href;    
  var url2 = replaceUrlParam (url, 'table_num', maxt); 
  window.location.href = url2;

  return 200;
};

//------------------------------------------------------------------------------------------------
function replaceUrlParam(url, paramName, max_t)
{

    var value = GetURLParameter(paramName);
    
     if (value == null) {
        value = 0;
      }
    var value = parseInt(value, 10);
    value = value + 1;
    if (max_t == 100 && paramName=="table_num") {
       value = 0;
    }
    
    if (value >= max_t) {

      
      url = replaceUrlParam (url, 'paper', 100);
      var value = 0;
    }
 
    var pattern = new RegExp('\\b('+paramName+'=).*?(&|#|$)');
    if (url.search(pattern)>=0) {
        return url.replace(pattern,'$1' + value + '$2');
    }
    url = url.replace(/[?#]$/,'');
    return url + (url.indexOf('?')>0 ? '&' : '?') + paramName + '=' + value;
};

//------------------------------------------------------------------------------------------------
function GetURLParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) 
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) 
        {
            return sParameterName[1];
        }
    }
};

//------------------------------------------------------------------------------------------------
// Java image magnifier function 
function magnify(imgID, zoom) {
  var img, glass, w, h, bw;
  img = document.getElementById(imgID);
  /*create magnifier glass:*/
  glass = document.createElement("DIV");
  glass.setAttribute("class", "img-magnifier-glass");
  /*insert magnifier glass:*/
  img.parentElement.insertBefore(glass, img);
  /*set background properties for the magnifier glass:*/
  glass.style.backgroundImage = "url('" + img.src + "')";
  glass.style.backgroundRepeat = "no-repeat";
  glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
  bw = 3;
  w = glass.offsetWidth / 2;
  h = glass.offsetHeight / 2;
  /*execute a function when someone moves the magnifier glass over the image:*/
  glass.addEventListener("mousemove", moveMagnifier);
  img.addEventListener("mousemove", moveMagnifier);
  /*and also for touch screens:*/
  glass.addEventListener("touchmove", moveMagnifier);
  img.addEventListener("touchmove", moveMagnifier);
  function moveMagnifier(e) {
    var pos, x, y;
    /*prevent any other actions that may occur when moving over the image*/
    e.preventDefault();
    /*get the cursor's x and y positions:*/
    pos = getCursorPos(e);
    x = pos.x;
    y = pos.y;
    /*prevent the magnifier glass from being positioned outside the image:*/
    if (x > img.width - (w / zoom)) {x = img.width - (w / zoom);}
    if (x < w / zoom) {x = w / zoom;}
    if (y > img.height - (h / zoom)) {y = img.height - (h / zoom);}
    if (y < h / zoom) {y = h / zoom;}
    /*set the position of the magnifier glass:*/
    glass.style.left = (x - w) + "px";
    glass.style.top = (y - h) + "px";
    /*display what the magnifier glass "sees":*/
    glass.style.backgroundPosition = "-" + ((x * zoom) - w + bw) + "px -" + ((y * zoom) - h + bw) + "px";
  }
  function getCursorPos(e) {
    var a, x = 0, y = 0;
    e = e || window.event;
    /*get the x and y positions of the image:*/
    a = img.getBoundingClientRect();
    /*calculate the cursor's x and y coordinates, relative to the image:*/
    x = e.pageX - a.left;
    y = e.pageY - a.top;
    /*consider any page scrolling:*/
    x = x - window.pageXOffset;
    y = y - window.pageYOffset;
    return {x : x, y : y};
  }
};

function Ignore() {
   // reload page
   var maxt = $('#my-data').data('value')
   var url = window.location.href;    
   var url2 = replaceUrlParam (url, 'table_num', maxt);
   
   window.location.href = url2;
  console.log("Table Deleted")
  return 200;
};

//------------------------------------------------------------------------------------------------
function applyAll() {
  var x = document.getElementById("concept").value; 
  var table = document.getElementById("pdf");
  var r = document.getElementById("pdf").rows.length;
  for (i=1; i<r; i++) {
      table.rows[i].cells[0].innerHTML = x
  }
  
  return false

};

//------------------------------------------------------------------------------------------------
function ClearAll() {
  
  var table = document.getElementById("pdf");
  var r = document.getElementById("pdf").rows.length;
  for (i=1; i<r; i++) {
      table.rows[i].cells[0].innerHTML = ""
  }
  
  return false

};

