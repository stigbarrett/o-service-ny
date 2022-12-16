//$.ajaxSetup({
//    async: false
//});

//var dropdownval = {

var dropdown = {
    loebnr: $('#select_konkurrence'),
    bane: $('#select_bane'),
};

var send = {
    konkurrence: dropdown.loebnr.val()
};

const konkurrence = dropdown.loebnr.val()

var loebnrorg = dropdown.loebnr.val();
var baneorg = dropdown.bane.val();
//console.log('Nu er vi her 2', baneorg);

var gridOptions = {
    rowHeight : 50,
    defaultColDef: {
        filter: false,
        cellRenderer: function(params) {
            return params.value ? params.value : '';
        },
    },
    sideBar: {
        toolPanels: [
        {
            id: 'filters',
            labelDefault: 'Filters',
            labelKey: 'filters',
            iconKey: 'filter',
            toolPanel: 'agFiltersToolPanel',
            toolPanelParams: {
            suppressExpandAll: true,
            suppressFilterSearch: true,
            },
        },
        ],
        defaultToolPanel: '',
    },
};

//const url4 = "/beregn/_get_otrack_link/"+loebnrorg;


function updateOtrack() {
    const url4 = "/beregn/_get_otrack_link/"+loebnrorg;
    $.get(url4, function (data) {
        console.log(data);
    
        const a = document.querySelector('#overskrift');
        a.href = data;
    });

};


function newGrid(url3) {
    
    var gridDiv = document.querySelector('#myGrid');
    var test = new agGrid.Grid(gridDiv, gridOptions);
    agGrid.simpleHttpRequest({url: url3}).then(function(data) {
        console.log(data);
        var kolonner = data[0];
        console.log(kolonner)
        gridOptions.api.setColumnDefs(kolonner);
        var raekker = data[1];
        gridOptions.api.setRowData(raekker);
    });
};

function recreateGrid(url3) {
    gridOptions.api.destroy();
    newGrid(url3);
};

function strakNy() {   
    var dropdownval = {
        loebnr: $('#select_konkurrence'),
        bane: $('#select_bane'),
    };
    
    var loebnrorg = dropdownval.loebnr.val();
    var baneorg = dropdownval.bane.val();
    const url3 = "/resultater/_get_strak_data/"+loebnrorg+"/"+baneorg; 
    
    recreateGrid(url3);
};


function resultat() {
    var dropdownval = {
        loebnr: $('#select_konkurrence'),
        bane: $('#select_bane'),
    };
    var loebnrorg = dropdownval.loebnr.val();
    var baneorg = dropdownval.bane.val();
    console.log("det er den her")
    const url4 = "/resultater/_get_resultat_data/"+loebnrorg+"/"+baneorg;
    recreateGrid(url4);
    };


//setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function() {
    const url3 = "/resultater/_get_strak_data/"+loebnrorg+"/"+baneorg;
    newGrid(url3);
});
    
// function to call XHR and update county dropdown

// event listener to state dropdown change


$(function() {
			
    // jQuery selection for  select box baner
    var dropdown = {
        konkurrence: $('#select_konkurrence'),
        bane: $('#select_bane')
    };

    // call to update on load
    
    updateBanerne();

    // function to call XHR and update county dropdown
    async function updateBanerne() {
        var send = {
            konkurrence: dropdown.konkurrence.val()
        };
        var konkurrence = dropdown.konkurrence.val()
        console.log('send');
        console.log(konkurrence);

        //dropdown.bane.attr('disabled', 'disabled');
        //dropdown.bane.empty();
        var testdata = $.getJSON("/resultater/_get_XMLbaner/"+konkurrence);
        console.log(testdata);
        console.log('stig')
        $.getJSON("/resultater/_get_XMLbaner/"+konkurrence), function(data) {
            data.forEach(function(item) {
                console.log(item);
                dropdown.bane.append(
                    $('<option>', {
                        value: item[0],
                        text: item[1]
                    })
                );
                
            });
            
            dropdown.bane.removeAttr('disabled');
        };
    }
    
    // event listener to state dropdown change
    $(document).ready(function(){
        dropdown.konkurrence.on('change', function() {
            console.log('opdaterbanerne')
            updateBanerne();
        });
    })
    
});
    




//document.addEventListener('DOMContentLoaded', function() {
//    const url3 = "/resultater/_get_strak_data/"+loebnrorg+"/"+baneorg;
//    newGrid(url3);
//});

//$(document).ready(function(){
//    dropdown.konkurrence.on('change', function() {
//    updateOtrack();
//    console.log('Opdater Otrack')
    
//    });
//})