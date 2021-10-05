
function html2json() {
  var $table = $("table")
  rows = [],
  header = [];
  conceptb_check = 0;
  conceptt_check = 0;
  $table.find("thead th").each(function () {
      header.push($(this).html());
  });
  
  $table.find("tbody tr").each(function () {
      var row = {};

      $(this).find("td").each(function (i) {
          var key = header[i],
              value = $(this).html();
              if (value) {

                if (typeof value === 'string' || value instanceof String) {
                  if (value.toUpperCase() == "CONCEPTB" || value.toUpperCase() == "META-ANALYSIS") {
                    conceptb_check = 1;
                  };
                  if (value.toUpperCase() == "CONCEPT THEME") {
                    conceptt_check = 1;
                  };

                };


              } else {
                value = ""
              };

          row[key] = value;
      });
    
      rows.push(row);
  });

  if (conceptb_check == 0) {
    var r = window.confirm("Missing 'ConceptB' column in the table. Do you want to continue?");
    if (r== false){
      return 0;
    };
  };

  if (conceptt_check == 0) {
    var r = window.confirm("Missing 'Concept Theme' column. This table may not be added to the list.");
    if (r== false){
      return 0;
    };
  };

  document.getElementById("concept_form").submit()
  var ref_con =  $("#ref_con").val();
  var con_cat =  $("#con_cat").val();
  var con_dir =  $("#con_dir option:selected").text();
  var eff_type =  $("#eff_type option:selected").text();
  var pub_doi = document.getElementById("pub_data").getAttribute('value');
  var table_num = document.getElementById("table_number").getAttribute('value');
  
  //construct an HTTP request
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/post_json', false);
  //xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
  var send_data ="table=" + JSON.stringify(rows,null,"") + "&Ref_Con="+ ref_con +
                  "&Con_Cat=" + con_cat + "&Con_Dir=" + con_dir + "&Eff_Type=" + eff_type +
                  "&DOI=" + pub_doi + "&Table_num=" + table_num;
  
  // send the collected data as JSON
  xhr.send(send_data);

  // reload page
  var maxt = $('#my-data').data('value');
  var url = window.location.href;    
  var url2 = replaceUrlParam (url, 'table_num', maxt); 
  window.location.href = url2;

  return 200;
};

//------------------------------------------------------------------------------------------------
function ignore_table() {
  
  var pub_doi = document.getElementById("pub_data").getAttribute('value');
  var table_num = document.getElementById("table_number").getAttribute('value');
  
  //construct an HTTP request
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/ignore_json', true);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
  var send_data ="&DOI=" + pub_doi + "&Table_num=" + table_num;
  
  // send the collected data as JSON
  xhr.send(send_data);

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
      //alert ("processing tables for next paper");
      window.alert("To process next paper (if any) click 'Review Extracted tables'");
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

//------------------------------------------------------------------------------------------------
function applyAll() {
  var x = document.getElementById("concept").value; 
  var table = document.getElementById("pdf");
  var r = document.getElementById("pdf").rows.length;
  for (i=2; i<r; i++) {
      table.rows[i].cells[0].innerHTML = x
  }
  
  return false

};

//------------------------------------------------------------------------------------------------
function ClearAll() {
  
  var table = document.getElementById("pdf");
  var r = document.getElementById("pdf").rows.length;
  for (i=2; i<r; i++) {
      table.rows[i].cells[0].innerHTML = ""
  }
  
  return false

};

