function getDay() {
    var now = new Date();
    var start = new Date(now.getFullYear(), 0, 0);
    var diff = (now - start) + ((start.getTimezoneOffset() - now.getTimezoneOffset()) * 60 * 1000);
    return Math.floor(diff / (1000 * 60 * 60 * 24));
}

var DATASET_STYLES = [
    {
        // actual
        borderColor: "#0ea5e9",
        backgroundColor: "rgba(14, 165, 233, 0.10)",
        borderWidth: 2.5,
        pointRadius: 0,
        pointHitRadius: 8,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: "#0ea5e9",
        pointHoverBorderColor: "#ffffff",
        pointHoverBorderWidth: 2,
        fill: true,
        lineTension: 0.25
    },
    {
        // target
        borderColor: "rgba(139, 92, 246, 0.55)",
        backgroundColor: "transparent",
        borderWidth: 1.5,
        borderDash: [4, 4],
        pointRadius: 0,
        pointHitRadius: 0,
        fill: false,
        lineTension: 0
    }
];

var LABELS = (function () {
    var arr = [];
    for (var i = 1; i <= 365; i++) arr.push(i);
    return arr;
})();

function getChart(index, data) {
    var id = "myChart" + index;
    var datasets = data.datasets.map(function (item, i) {
        var style = DATASET_STYLES[i] || DATASET_STYLES[0];
        var ds = {
            label: item.label,
            data: item.data
        };
        for (var k in style) if (Object.prototype.hasOwnProperty.call(style, k)) ds[k] = style[k];
        return ds;
    });

    var annotations = [];
    if (window.IS_CURRENT_YEAR) {
        annotations.push({
            drawTime: "afterDatasetsDraw",
            type: "line",
            mode: "vertical",
            scaleID: "x-axis-0",
            value: getDay(),
            borderWidth: 1,
            borderColor: "rgba(236, 72, 153, 0.55)",
            borderDash: [3, 3],
            label: {
                content: "TODAY",
                enabled: true,
                position: "top",
                backgroundColor: "rgba(236, 72, 153, 0.95)",
                fontColor: "#ffffff",
                fontSize: 9,
                fontStyle: "bold",
                xPadding: 6,
                yPadding: 2,
                cornerRadius: 4
            }
        });
    }

    var ctx = document.getElementById(id).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: { labels: LABELS, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            legend: { display: false },
            tooltips: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(255, 255, 255, 0.98)',
                titleFontColor: '#0f172a',
                titleFontSize: 11,
                titleFontStyle: '600',
                bodyFontColor: '#0f172a',
                bodyFontSize: 11,
                borderColor: 'rgba(15, 23, 42, 0.10)',
                borderWidth: 1,
                cornerRadius: 6,
                xPadding: 10,
                yPadding: 8,
                displayColors: true,
                callbacks: {
                    title: function (items) { return 'day ' + items[0].xLabel; },
                    label: function (item, d) {
                        var label = d.datasets[item.datasetIndex].label;
                        var value = item.datasetIndex === 0
                            ? Math.round(item.yLabel)
                            : Math.round(item.yLabel * 10) / 10;
                        return label + ': ' + value;
                    }
                }
            },
            hover: { mode: 'index', intersect: false },
            scales: {
                xAxes: [{
                    gridLines: {
                        color: 'rgba(15, 23, 42, 0.06)',
                        zeroLineColor: 'rgba(15, 23, 42, 0.06)',
                        drawBorder: false
                    },
                    ticks: {
                        fontColor: '#94a3b8',
                        fontSize: 10,
                        autoSkip: true,
                        maxTicksLimit: 7,
                        padding: 4
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgba(15, 23, 42, 0.06)',
                        zeroLineColor: 'rgba(15, 23, 42, 0.06)',
                        drawBorder: false
                    },
                    ticks: {
                        fontColor: '#94a3b8',
                        fontSize: 10,
                        beginAtZero: true,
                        precision: 0,
                        padding: 4,
                        maxTicksLimit: 5
                    }
                }]
            },
            annotation: { annotations: annotations }
        }
    });
}
