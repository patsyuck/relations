// This is adapted from https://bl.ocks.org/mbostock/2675ff61ea5e063ede2b5d63c08020c7

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
        return d.id;
    }))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

d3.json("../json/graph.json", function (error, graph) {
    if (error) throw error;

    var link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke", color)
        .attr("stroke-width", 3);

    var marker = svg.append("marker")
        .attr("id", "resolved")
        .attr("markerUnits","userSpaceOnUse")
        .attr("viewBox", "0 -5 10 10")//The area of ​​the coordinate system
        .attr("refX", 15)//Arrow coordinates
        .attr("refY", 0)
        .attr("markerWidth", 12)//marker size
        .attr("markerHeight", 12)
        .attr("orient", "auto")//Drawing direction, can be set to: auto (automatically confirm the direction) and angle value
        .attr("stroke-width", 2)//arrow width
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")//The path of the arrow
        .attr('fill', 'black');//arrow color


    var node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("cursor", "pointer")
        .attr("r", degree)
        /*.attr("r", 5)*/
        .attr("fill", colour)
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged));
            /*.on("end", dragended));*/

    /*var node = svg.append("g")
        .attr("class", "nodes")
        .data(graph.nodes);

    var node = nodeG.selectAll("g").data(graph.nodes);

    var nodeEnter = node.
        enter().append("g")
        .call(drag);

    node.exit().remove();
            
    nodeEnter.append("rect")
        .attr("class", "node-rect")
        .attr("y", -nodeSize)
        .attr("height", nodeSize * 2)
        .attr("rx", nodeSize)
        .attr("ry", nodeSize)
        .on("click", function (d){
            simulation.unfix(d);
        });
            
    nodeEnter.append("text")
        .attr("class", "node-text");
            
    node = node.merge(nodeEnter);
            
    node.select(".node-text")
        .text(function (d){ return d.name; })
        .each(function (d) {
              
        var circleWidth = nodeSize * 2,
            textLength = this.getComputedTextLength(),
            textWidth = textLength + nodeSize;
              
        if(circleWidth > textWidth) {
            d.isCircle = true;
            d.rectX = -nodeSize;
            d.rectWidth = circleWidth;
        } else {
            d.isCircle = false;
            d.rectX = -(textLength + nodeSize) / 2;
            d.rectWidth = textWidth;
            d.textLength = textLength;
        }
    });
            
    node.select(".node-rect")
        .attr("x", function(d) { return d.rectX; })
        .attr("width", function(d) { return d.rectWidth; });*/

    // видимий текст, який починається в центрі вузла            
    /*var myText = svg.selectAll(".mytext")
        .data(graph.nodes)
        .enter().append("text")
        .style("fill", "#0000ff")
        .text(function (d) {
            if (d.colour === "white")
                return d.name
            else
                return d.name + " (" + d.edrpou + ")"
        });*/

    // видимий текст, який відцентровано по центру вузла
    /*var text = svg.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(graph.nodes)
        .enter().append("text")
        .style("fill", "#0000ff")
        .style("dominant-baseline", "central")
        .style("text-anchor", "middle")
        .style("font-family", "sans-serif")
        .style("font-size", "0.7em")
        .text(function (d) {
            if (d.colour === "white")
                return d.name
            else
                return d.name + " (" + d.edrpou + ")"
        });*/

    // текст, який стає видимим при наведенні курсора на центр вузла
    node.append("title")
        .text(function (d) {
            if (d.colour === "white")
                return d.name
            else
                return d.name + " (" + d.edrpou + ")"
        });

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            })
            .attr("marker-end", "url(#resolved)");
            // останній атрибут для відмальовки стрілочок!

        node
            .attr("cx", function (d) {
                return d.x;
            })
            .attr("cy", function (d) {
                return d.y;
            });
            /*.attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
              });*/

        // координати для розміщення тексту 
        myText
            .attr("x", function(d) { 
                return d.x; 
            })
            .attr("y", function(d) { 
                return d.y; 
            });

        /*text
            .attr("transform", function(d) {
              return "translate(" + d.x + "," + d.y + ")";
            });*/

    }
});

function color(d) {
    return d.color;
}

function colour(d) {
    return d.colour;
}

function degree(d) {
    return d.degree + 4;
}

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}