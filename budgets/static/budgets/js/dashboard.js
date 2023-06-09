function loadData(request) {
    let data =JSON.parse(request.responseText);
    document.getElementById("numAccounts").innerHTML=data.stats.num_accounts;
    document.getElementById("totalBudget").innerHTML=data.stats.total_budget;
    document.getElementById("remainingBudget").innerHTML=data.stats.remaining_budget;
    document.getElementById("expenses").innerHTML=data.stats.expenses;

    if(data.stats.remaining_budget <=0){
        document.getElementById("statRemaining").classList.remove('bg-success');
        document.getElementById("statRemaining").classList.add('bg-danger');
    }

    createHistoryChart(data.charts.history);
}

function createHistoryChart(data) {

    Morris.Area({
      element: 'chart',
      data: data.series,
      xkey: 'x',
//      parseTime: false,
//      xLabelFormat: function(obj){
//        var index = obj.x < 12 ? obj.x : (obj.x -12);
//        return xlabel[index];
//      },
      ykeys: data.ykeys,
      labels: data.labels,
    });
}