// TODO Here we need to get the JSON data from the file
var list = [
    {"Stock": "AAPL", "Quantity": "100", "Price": "20", "Gain/Loss": "-20%"},
    {"Stock": "GME", "Quantity": "50", "Price": "10", "Gain/Loss": "1%"},
    {"Stock": "TSLA", "Quantity": "33", "Price": "5", "Gain/Loss": "12%"}
];

function jsonReader(filePath, cb) {
    fs.readFile(filePath, 'utf8', (err, fileData) => {
        if (err) {
            return cb && cb(err);
        }
        try {
            const object = JSON.parse(fileData);
            return cb && cb(null, object);
        } catch (err) {
            return cb && cb(err);
        }
    });
}

jsonReader("./portfolio.json", (err) => {
    if (err) {
        console.log(err);
    }
});

function constructTable(selector) {

    // Getting the all column names
    let cols = Headers(list, selector);

    // Traversing the JSON data
    for (let i = 0; i < list.length; i++) {
        let row = $('<tr/>');
        for (let colIndex = 0; colIndex < cols.length; colIndex++) {
            let val = list[i][cols[colIndex]];

            // If there is any key, which is matching
            // with the column name
            if (val == null) val = "";
            row.append($('<td/>').html(val));
        }

        // Adding each row to the table
        $(selector).append(row);
    }
}

function Headers(list, selector) {
    let columns = [];
    let header = $('<tr/>');

    for (let i = 0; i < list.length; i++) {
        let row = list[i];

        for (let k in row) {
            if ($.inArray(k, columns) === -1) {
                columns.push(k);

                // Creating the header
                header.append($('<th style="width:120px"/>').html(k));
            }
        }
    }

    // Appending the header to the table
    $(selector).append(header);
    return columns;
}