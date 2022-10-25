function portfolioTable(table, pf){
    let portHeader = table.createTHead();
    let headRow = table.insertRow();
    for (let entry of pf) {
        let th = document.createElement('th');
        let text = doculment.createTextNode(entry);
        th.appendChild(text);
        headRow.appendChild(th);
    }
}

let portTable = document.querySelector("table");
let pf = {{ Portfolio}}
portfolioTable(portTable, pf);