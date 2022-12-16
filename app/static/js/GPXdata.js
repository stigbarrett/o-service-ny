var dropdown = {
    loebnr: $('#loeb'),
    bane: $('#baner'),
};

var dropdownval = dropdown;

var loebnrorg = dropdownval.loebnr.val();
var baneorg = dropdownval.bane.val();

let banedataID = document.getElementById('banedata_id').value;
let CSFR_data = document.getElementById('csfr_token')
//const url3 = "{{url_for('tilmelding.data1', baneresultatID='idher')}}".replace("idher", banedataID);
const url3 = "/resultater/data1/"+banedataID;
const url8 = "/resultater/update";


console.log('Nu er vi her 2', baneorg);

var gridOptionsOLD = {
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

const gridOptions = {
    columnDefs: [
        {
            field: 'id', maxWidth: 60,
            suppressColumnsToolPanel: true,
            hide: true,
        },
        { field: 'Post', maxWidth: 100 },
        {
            headerName: 'Status',
            field: 'Status',
            maxwidth: 100,
            cellEditor: 'agRichSelectCellEditor',
            cellEditorPopup: true,
            cellEditorParams: {
              values: ['OK', 'ejOK'],
            },
          },
        { headerName: 'Afstand fra Post', field: 'Afstand', maxWidth: 120 },
        { headerName: 'Stræk tid', field: 'Straektid', maxwidth: 100 },
        { headerName: 'Samlet tid', field: 'Samlet', maxWidth: 100 },
        { headerName: 'Stræk distance', field: 'Straek', maxWidth: 120 },
        { headerName: 'Samlet distance', field: 'Distance', maxWidth: 120 },
    ],
    defaultColDef: {
      flex: 1,
      minWidth: 100,
    },
    
    onCellValueChanged: onCellValueChanged,
    
    defaultColDef: {
        flex: 1,
        resizable: true,
        editable: true,
        },
    
    };

    
function onCellValueChanged(event) {
    console.log('Data after change is', event.data);
    let data = event.data;
    console.log(data);
    console.log(CSFR_data);
    (async () => {
        const rawResponse = await fetch(url8, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': CSFR_data.value,
          },
          body: JSON.stringify(event.data)
        });
        const content = await rawResponse.json();
      
        console.log(content);
      })();
    

      };

const url4 = "/beregn/_get_otrack_link/"+loebnrorg;


$.get(url4, function (data) {
    console.log(data);
    
    const a = document.querySelector('#overskrift');
    a.href = data;
});

function updateOtrack() {
    const url4 = "/beregn/_get_otrack_link/"+loebnrorg;
    $.get(url4, function (data) {
        console.log(data);
    
        const a = document.querySelector('#overskrift');
        a.href = data;
    });

};

function newGridOld() {
    const url1 = "/resultater/_get_GPX_postoversigt_kolonner/";
    const url2 = "{{url_for('tilmelding.data', baneresultatID='idher')}}".replace("idher", banedataID);
    //let retur_data = "/resultater/_get_test_data/";
    console.log('Nu er vi her');
    var gridDiv = document.querySelector('#myGrid');
    var test = new agGrid.Grid(gridDiv, gridOptions);
    agGrid.simpleHttpRequest({url: url1}).then(function(data) {
    gridOptions.api.setColumnDefs(data);
    console.log(data);
    });
    agGrid.simpleHttpRequest({url: url2}).then(function(data) {
        gridOptions.api.setRowData(data);
    });
};

function newGridOLD(url3) {
    
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

function newGrid(url3) {
    
    var gridDiv = document.querySelector('#myGrid');
    var test = new agGrid.Grid(gridDiv, gridOptions);
    agGrid.simpleHttpRequest({url: url3}).then(function(data) {
        var raekker = data;
        console.log(raekker);
        gridOptions.api.setRowData(raekker);
    });
};

function recreateGrid(url3) {
    gridOptions.api.destroy();
    newGrid(url3);
};

function strakNy() {   
    var dropdownval = {
        loebnr: $('#loeb'),
        bane: $('#baner'),
    };
    
    var loebnrorg = dropdownval.loebnr.val();
    var baneorg = dropdownval.bane.val();
    const url3 = "/resultater/_get_strak_data/"+loebnrorg+"/"+baneorg; 
    
    recreateGrid(url3);
};

function resultat() {
    var dropdownval = {
        loebnr: $('#loeb'),
        bane: $('#baner'),
    };
    var loebnrorg = dropdownval.loebnr.val();
    var baneorg = dropdownval.bane.val();
    console.log("det er den her")
    const url4 = "/resultater/_get_resultat_data/"+loebnrorg+"/"+baneorg;
    recreateGrid(url4);
    };

//setup the grid after the page has finished loading

document.addEventListener('DOMContentLoaded', function() {
    console.log('Nu er vi her 3');
    newGrid(url3);
});

//$(document).ready(function(){
//    dropdown.konkurrence.on('change', function() {
//    updateOtrack();
//    console.log('Opdater Otrack')
    
//    });
//})