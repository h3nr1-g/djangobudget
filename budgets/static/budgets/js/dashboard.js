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

    createHistoryChart(data.charts.history, data.lang);
}

function createHistoryChart(data, lang) {

    Morris.Area({
      element: 'chart',
      data: data.series,
      xkey: 'x',
      xLabelFormat: function (x) {
        return x.toLocaleDateString(lang, {year:"numeric", month:"numeric", day:"numeric"});
      },
      ykeys: data.ykeys,
      labels: data.labels,
    });
}