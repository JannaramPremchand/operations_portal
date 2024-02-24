
$(function() {
  var oTable=$('#datatable').DataTable({
    "oLanguage": {
      "sSearch": "Filter Data"
    },
    "iDisplayLength": -1,
    "sPaginationType": "full_numbers",
	 "fnFooterCallback": function ( nRow, aaData, iDataStart, iDataEnd ) {
			/* Calculate the total market share for all browsers in this table (ie inc. outside
			 * the pagination
			 */
			var iTotalMarket = 0;
			for ( var i=0 ; i<aaData.length ; i++ )
			{
				iTotalMarket += aaData[i][4]*1;
			}
			
			/* Calculate the market share for browsers on this page */
			var iPageMarket = 0;
			for ( var i=iDataStart ; i<iDataEnd ; i++ )
			{
				iPageMarket += aaData[i][4]*1;
			}
			function secondsToHms(d) {
				d = Number(d);
                var h = Math.floor(d / 3600);
                var m = Math.floor(d % 3600 / 60);
                var s = Math.floor(d % 3600 % 60);

                var hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
                var mDisplay = m > 0 ? m + (m == 1 ? " minute, " : " minutes, ") : "";
                var sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
                return hDisplay + mDisplay + sDisplay; 
                    }
             var hms_duration = secondsToHms(iPageMarket)
			/* Modify the footer row to match what we want */
			var nCells = nRow.getElementsByTagName('th');
			// nCells[3].innerHTML = 'Total';
			// nCells[4].innerHTML = hms_duration;
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
      aData._date = new Date(aData[5]).getTime()
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


