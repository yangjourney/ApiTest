//Handle result format
try{
	$elements = $(".json").each(function(){
        var data = $(this).html().replace(/\field/g).replace(/\expected/g,"期望结果").replace(/\actual/g,"实际结果");
        if(data != ''){
            $(this).html(FormatJSON(JSON.parse(data),"    "));
            hljs.highlightBlock(this);
        }
       
	});
	
}catch(e){}

function FormatJSON(oData, sIndent) {
    if (arguments.length < 2) {
        var sIndent = "";
    }
    var sIndentStyle = "    ";
    var sDataType = RealTypeOf(oData);

    // open object
    if (sDataType == "array") {
        if (oData.length == 0) {
            return "[]";
        }
        var sHTML = "[";
    } else {
        var iCount = 0;
        $.each(oData, function() {
            iCount++;
            return;
        });
        if (iCount == 0) { // object is empty
            return "{}";
        }
        var sHTML = "{";
    }

    // loop through items
    var iCount = 0;
    $.each(oData, function(sKey, vValue) {
        if (iCount > 0) {
            sHTML += ",";
        }
        if (sDataType == "array") {
            sHTML += ("\n" + sIndent + sIndentStyle);
        } else {
            sHTML += ("\n" + sIndent + sIndentStyle + "\"" + sKey + "\"" + ": ");
        }

        // display relevant data type
        switch (RealTypeOf(vValue)) {
            case "array":
            case "object":
                sHTML += FormatJSON(vValue, (sIndent + sIndentStyle));
                break;
            case "boolean":
            case "number":
                sHTML += vValue.toString();
                break;
            case "null":
                sHTML += "null";
                break;
            case "string":
                sHTML += ("\"" + vValue + "\"");
                break;
            default:
                sHTML += ("TYPEOF: " + typeof(vValue));
        }

        // loop
        iCount++;
    });

    // close object
    if (sDataType == "array") {
        sHTML += ("\n" + sIndent + "]");
    } else {
        sHTML += ("\n" + sIndent + "}");
    }

    // return
    return sHTML;
}

function RealTypeOf(v) {
  if (typeof(v) == "object") {
    if (v === null) return "null";
    if (v.constructor == (new Array).constructor) return "array";
    if (v.constructor == (new Date).constructor) return "date";
    if (v.constructor == (new RegExp).constructor) return "regex";
    return "object";
  }
  return typeof(v);
}
    
    $(".json-body").bind("blur",function(e){
        JSON.parse
        console.log($(this).value);
    });
    $("#add").click(function(e){
        var expected_name = $(this).parents().find(".expected_name").val();
        var expected_value = $(this).parents().find(".expected_value").val();
        if($("#expected").val().length > 10){
            $("#expected").val($("#expected").val()+',{"query": "'+expected_name+'","expected": "'+expected_value+'"}\n');
        }else{
            $("#expected").val($("#expected").val()+'{"query": "'+expected_name+'","expected": "'+expected_value+'"}\n');
        }
        
    });
    
    $("#clear").click(function(e){
        $("#expected").val("");
    });
    $("a[data-toggle='tooltip']").tooltip();

$.fn.autocomplete.Constructor.prototype.blur = function() {
      var that = this;
      setTimeout(function () { that.hide() }, 500);
   };
var statuses = [{
    status:"200",
    msg:"请求成功",
    en:"OK"
    },{
    status:"401",
    msg:"未授权",
    en:"Unauthorized"
    },{
    status:"403",
    msg:"禁止访问",
    en:"Forbidden"
    },{
    status:"404",
    msg:"找不到资源",
    en:"Not Found"
    },{
    status:"405",
    msg:"方法禁用",
    en:"Method Not Allowed"
    },{
    status:"408",
    msg:"请求超时",
    en:"Request Timeout"
    },{
    status:"415",
    msg:"不支持的请求格式",
    en:"Unsupported Media Type"
    },{
    status:"500",
    msg:"内部错误",
    en:"Internal Server Error"
    }];
//autocomplete
$("#expected_status").bind("keydown",function(e){ //获取文本框的实际值
        $(this).autocomplete({
        source:statuses,
        formatItem:function(item){
            return item["status"]+"("+item["en"]+","+item["msg"]+")";
        },
        setValue:function(item){
            return {'data-value':item["status"],'real-value':item["status"]};
        }
    });
    });