// Read the CSV data and call drawChart
function readAndDrawChart(csvFileName, description) {
    d3.csv(csvFileName).then(data => {
        const transformer = data[0][Object.keys(data[0])[1]];
        data = data.filter(d => d["Description"] === description);

        data.forEach(d => {
            d.timestamp = d3.timeParse("%Y-%m-%d %H:%M:%S")(d.timestamp);
            d.original_values = +d.original_values;
            d.average_original = +d.average_original;
            d.upper_quartile_original = +d.upper_quartile_original;
            d.future_values = +d.future_values;
            d.average_future = +d.average_future;
            d.worst_case = +d.worst_case;
        });

        drawChart(data, transformer);
    });
}

// Draw the chart
function drawChart(data, transformer) {
    d3.select("#chart").html("");
    // Create chart dimensions
    const margin = { top: 30, right: 20, bottom: 60, left: 50 };
    const width = Math.min(960, window.innerWidth) - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;
    
    const svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Create axes, labels, and title
    const x = d3.scaleTime().range([0, width]);
    const y = d3.scaleLinear().range([height, 0]);
    x.domain(d3.extent(data, d => d.timestamp));
    y.domain([0, d3.max(data, d => Math.max(d.original_values, d.average_original, d.upper_quartile_original, d.future_values, d.average_future, d.worst_case))]);
    svg.append("g").attr("transform", "translate(0," + height + ")").call(d3.axisBottom(x));
    svg.append("g").call(d3.axisLeft(y));
    
    // Add x-axis label
    svg.append("text")
        .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.top + 10) + ")")
        .text("Time (7-day period, where available)").style("text-anchor", "middle");

    // Add y-axis label
    svg.append("text")
        .attr("y", 0 - margin.left).attr("x",0 - (height / 2))
        .attr("dy", "1em").attr("transform", "rotate(-90)")
        .text("Load, kW").style("text-anchor", "middle");
    
    // Add the chart title
    svg.append("text")
        .attr("x", (width / 2)).attr("y", 0 - (margin.top / 2))
        .html("Load profile for " + transformer).style("font-size", "1.17em").attr("text-anchor", "middle");

    // Add maps link
    const locationName = transformer.slice(transformer.indexOf(' - ') + 3);
    const mapsUrl = `https://maps.google.com/maps?q=${encodeURIComponent(locationName)}`;
    document.getElementById("substation-URL").innerHTML = "<a href=\"" + mapsUrl + "\" target=\"blank\">" + transformer + "</a>";


    // Draw 3 lines
    svg.append("path")
        .datum(data)
        .attr("id", "WorstCase")
        .attr("class", "tooltip-element")
        .attr("fill", "rgba(255, 165, 0, 0.1)")
        .attr("stroke", "orange")
        .attr("stroke-width", 0.5)
        .attr("d", d3.area()
            .x(d => x(d.timestamp))
            .y0(y(0))
            .y1(d => y(d.worst_case)));

    svg.append("path")
        .datum(data)
        .attr("id", "Future")
        .attr("class", "tooltip-element")
        .attr("fill", "rgba(70, 130, 180, 0.2)")
        .attr("stroke", "green")
        .attr("stroke-width", 0.5)
        .attr("d", d3.area()
            .x(d => x(d.timestamp))
            .y0(y(0))
            .y1(d => y(d.future_values)));
    
    svg.append("path")
        .datum(data)
        .attr("id", "OriginalValues")
        .attr("class", "tooltip-element")
        .attr("fill", "rgba(70, 130, 180, 0.6)")
        .attr("stroke", "steelblue")
        .attr("stroke-width", "0.8")
        .attr("d", d3.area()
            .x(d => x(d.timestamp))
            .y0(y(0))
            .y1(d => y(d.original_values)));

    // Add in the horizontal average and upper quartile lines
    svg.append("path")
        .datum(data)
        .attr("id", "AverageFuture")
        .attr("class", "tooltip-element")
        .attr("fill", "none")
        .attr("stroke", "green")
        .attr("stroke-width", 1.5)
        .attr("d", d3.area()
            .x(d => x(d.timestamp))
            .y(d => y(d.average_future)));

    svg.append("path")
        .datum(data)
        .attr("id", "AverageOriginal")
        .attr("class", "tooltip-element")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", d3.area()
            .x(d => x(d.timestamp))
            .y(d => y(d.average_original)));

    svg.append("path")
        .datum(data)
        .attr("id", "AverageUpperQuartileOriginal")
        .attr("class", "tooltip-element")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", d3.area()
            .x(d => x(d.timestamp))
            .y(d => y(d.upper_quartile_original)));

    // Tooltip code
    const averageValue = data[0].average_original.toFixed(2);
    const upperQuartileValue = data[0].upper_quartile_original.toFixed(2);
    const futureAverageValue = data[0].average_future.toFixed(2);
    const peakValue = d3.max(data, d => d.original_values).toFixed(2);
    const peakValue_worst = d3.max(data, d => d.worst_case).toFixed(2);

    var tooltip = d3.select("#chart")
        .append("div")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("width", "250px")
        .style("background", "rgba(255, 255, 255, 0.8)")
        .style("border-radius", "5px")
        .style("padding", "7px 12px")
        .style("font-size", "14px")
        .style("pointer-events", "none")
        .text("Tooltip text goes here");

    d3.selectAll(".tooltip-element")
        .on("mouseover", function() {
            return tooltip.style("visibility", "visible");
        })
        .on("mousemove", function() {
            const rect = chart.getBoundingClientRect();
            tooltip.style("top", (event.pageY - rect.top - scrollY - 50) + "px").style("left", (event.pageX - rect.x + 20) + "px");
            if (this.id === "OriginalValues") {
                tooltip.html("<b>Todays load profile:</b> The one-week load profile of an 11kv transformer in the UK. They have about 50 houses connected to them, with a range of 3 - 300 houses.<br/><b>Average load:" + averageValue + "kW<br/>Peak load: " + peakValue + "kW</b>");
            } else if (this.id === "AverageOriginal") {
                tooltip.html("<b>Average (" + averageValue + "kW) and <br/>Upper Quartile (" + upperQuartileValue + "kW)</b><br/> load today, showing a utilisation factor of ~50%.");
            } else if (this.id === "Future") {
                tooltip.html("<b>Better future:</b> \"3x consumption, capped at the peak\" of the blue line. It's the maximum load-shifting we expect from heat pumps and EVs, before we need to upgrade the transformer. <br/><b>Average load:" + futureAverageValue + "kW<br> <b>Peak load: " + peakValue + "kW</b>");
            } else if (this.id === "WorstCase") {
                tooltip.html("<b>Current trajectory:</b> This is the same average as the green line, and the load profile of blue. Our peak load has increased 2x calling requiring upgrades on every street in the country.<br/><b>Average load:" + futureAverageValue + "kW<br> <b>Peak load: " + peakValue_worst + "kW</b>");
            } else if (this.id === "AverageFuture") {
                tooltip.html("<b>Average load possible: " + futureAverageValue + "</b><br/> Without upgrading transformers, we can achieveabout 2x the blue average. It shows how we could double electricity consumption without upgrading our transformers.");
            }
            return tooltip.style("visibility", "visible");
        })
        .on("mouseout", function() {
            return tooltip.style("visibility", "hidden");
        });
}


// Populate the different cable options:
const csvFileSelector = document.getElementById("csvFile");
const descriptionSelector = document.getElementById("description");

function updateDescriptionOptions(csvFileName) {
    d3.csv(csvFileName).then(data => {
        const descriptions = [...new Set(data.map(d => d["Description"]))];
        descriptionSelector.innerHTML = "";

        descriptions.forEach(desc => {
            const option = document.createElement("option");
            option.value = desc;
            option.textContent = desc;
            descriptionSelector.appendChild(option);
        });

        readAndDrawChart(csvFileName, descriptions[0]);
    });
}

csvFileSelector.addEventListener("change", () => {
    updateDescriptionOptions(csvFileSelector.value);
});

descriptionSelector.addEventListener("change", () => {
    readAndDrawChart(csvFileSelector.value, descriptionSelector.value);
});

updateDescriptionOptions(csvFileSelector.value);


