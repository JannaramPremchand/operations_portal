
$(function() {
  var oTable=$('#datatable').DataTable({
    "oLanguage": {
      "sSearch": "Filter Data"
    },
    "iDisplayLength": -1,
    "sPaginationType": "full_numbers",
	 "fnFooterCallback": function ( nRow, aaData, iDataStart, iDataEnd ) {

    const iTotalMarket = [];
			for ( var i=0 ; i<aaData.length ; i++ )
			{
				iTotalMarket.push(String(aaData[i][4]));
			}
			
			/* Calculate the market share for browsers on this page */
			const iPageMarket = [];
			for ( var i=iDataStart ; i<iDataEnd ; i++ )
			{
				iPageMarket.push(String(aaData[i][4]));
			}
      // console.log(iPageMarket)
      
      function sumTime(iPageMarket) {
        let sumSeconds = 0;
          
        iPageMarket.forEach(time => {
          let a = time.split(":");
          let seconds = +a[0] * 60 * 60 + +a[1] * 60 + +a[2];
          sumSeconds += seconds;
        });
          
        return new Date(sumSeconds * 1000).toISOString().substr(11, 8);
      }
          
      var hms_duration =  sumTime(iPageMarket);
      
			var nCells = nRow.getElementsByTagName('th');
			nCells[3].innerHTML = 'Total';
			nCells[4].innerHTML = hms_duration;
		}

  });

	
  $('#datepicker_from').click(function() {
    $("#datepicker_from").datepicker("show");
  });
  $('#datepicker_to').click(function() {
    $("#datepicker_to").datepicker("show");
  });


  $("#datepicker_from").datepicker({
    "onSelect": function(date) {
      minDateFilter = new Date(date).getTime();
      oTable.fnDraw();
    }
  }).keyup(function() {
    minDateFilter = new Date(this.value).getTime();
    oTable.fnDraw();
  });

  $("#datepicker_to").datepicker({
    "onSelect": function(date) {
      maxDateFilter = new Date(date).getTime();
      oTable.fnDraw();
    }
  }).keyup(function() {
    maxDateFilter = new Date(this.value).getTime();
    oTable.fnDraw();
  });
  
  $("#radio_date_filter input:radio").click(function(){
    
 
    var currentDate = new Date();

    if($(this).val() == 'week'){

      var weekDate = new Date();
      var first = weekDate.getDate() - 7;
      var firstDayofWeek = new Date(weekDate.setDate(first));
      minDateFilter = firstDayofWeek.getTime();
   
      
    }else{
      
       var monthDate = new Date();
       var firstDayOfMonth = new Date(monthDate.setMonth(monthDate.getMonth(),0));
       minDateFilter = firstDayOfMonth.getTime();
      
    }
  
    maxDateFilter = currentDate.getTime();
    oTable.fnDraw();
    
  });


});

// Date range filter
minDateFilter = "";
maxDateFilter = "";


$.fn.dataTableExt.afnFiltering.push(
  function(oSettings, aData, iDataIndex) {
   
    if (typeof aData._date == 'undefined') {
      aData._date = new Date(aData[1]).getTime()
    }

    if (minDateFilter && !isNaN(minDateFilter)) {
      if (aData._date < minDateFilter) {
        return false;
      }
    }

    if (maxDateFilter && !isNaN(maxDateFilter)) {
      if (aData._date > maxDateFilter) {
        return false;
      }
    }

    return true;
	
  }
);


