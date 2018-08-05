      var margin = { top: 50, right: 0, bottom: 50, left: 30 },
          width = 960 - margin.left - margin.right,
          height = 600 - margin.top - margin.bottom;
      var buckets = 10;
      var maxNum = 7.0;
      var poundPerKg = 2.20462;
      var oneKgMl = 2.5;

      var svg = d3.select("#plotarea").append("svg")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom)
              .append("g")
              .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var colors = colorbrewer.RdYlGn[buckets];
      colors[buckets-1] = "#999999";

      var colorScale = d3.scale.quantile()
          .domain([0,0.1,0.7,1,maxNum])
          .range(colors.reverse());

      var ghostLimits = {"humidityData": {"0": [[75, 75, 75, 75],
                                           [75, 75, 75, 75],
                                           [75, 75, 75, 75],
                                           [75, 75, 75, 75]],

                                     "1": [[55, 50, 45, 40],
                                           [50, 55, 50, 45],
                                           [50, 50, 55, 50],
                                           [50, 50, 50, 55]]},
                    "pressureData": {"0": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],
                                           [70, 70, 70, 75]],
                                     "1": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],
                                           [70, 70, 70, 75]],
                                     "2": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],
                                           [70, 70, 70, 75]],
                                     "3": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],
                                           [70, 70, 70, 75]],
                                     "4": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],
                                           [70, 70, 70, 75]],
                                     "5": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],
                                           [70, 70, 70, 75]]}};

      var oneKgRef = {"humidityData": {"0": [[200, 200, 200, 200],
                                           [200, 200, 200, 200],
                                           [200, 200, 200, 200],
                                           [200, 200, 200, 200]],

                                     "1": [[55, 50, 45, 40],
                                           [50, 55, 50, 45],
                                           [50, 50, 55, 50],
                                           [50, 50, 50, 55]]},
                    "pressureData": {"0": [[375, 320, 375, 335],
                                           [380, 320, 370, 350],
                                           [390, 320, 380, 380],
                                           [395, 350, 400, 400]],
                                     "1": [[370, 380, 385, 375],
                                           [400, 390, 400, 390],
                                           [390, 390, 390, 395],
                                           [385, 375, 360, 360]],
                                     "2": [[395, 370, 385, 400],
                                           [180, 185, 170, 180],
                                           [390, 375, 390, 405],
                                           [400, 355, 390, 400]],
                                     "3": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],  
                                           [70, 70, 70, 75]],
                                     "4": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],
                                           [70, 70, 70, 75]],
                                     "5": [[75, 70, 65, 60],
                                           [70, 75, 70, 65],
                                           [70, 70, 75, 70],
                                           [70, 70, 70, 75]]}};

      function weightScaling(val,refVal) {
        if (val < refVal) {
          return oneKgMl*(val/refVal);
        } else {
          return oneKgMl + 2*oneKgMl*(val-refVal)/(0.15*refVal);
        }
      }

      function moistureScaling(val,refVal) {
        if (val < refVal) {
          return poundPerKg*(val/refVal);
        } else {
          return poundPerKg + 2*poundPerKg*(val-refVal)/(0.15*refVal);
        }
      }

      function update() {
        // Fetch data from the endpoint
        var dataAPI = "https://pups.storm.gatech.edu/wsgi/portal/data";
        $.getJSON( dataAPI, { format: "json" })
            .done(function(jsonData) {

              var pressureData = jsonData.pressureData;
              var pNo = Object.keys(jsonData.pressureData).length;
              var hNo = Object.keys(jsonData.humidityData).length;
              var data =[];
              for (var i=0; i<pNo; i++) {
                for (var j=0; j<4; j++) {
                  for (var k=0; k<4; k++) {
                    if (i==0) {
                      var xPos = Math.floor(i)*4 + (k);
                      var yPos = j;
                    } else if (i==1) {
                      var xPos = Math.floor(i)*4 + (4-k-1);
                      var yPos = (4-j-1);
                    } else if (i==2) {
                      var xPos = Math.floor(i)*4 + (4-k-1);
                      var yPos = (4-j-1);
                    // } else if (i==3) {
                    //   var xPos = Math.floor(i/2)*4 + (4-k-1);
                    //   var yPos = (i%2)*4 + (4-j-1);
                    // } else if (i==4) {
                    //   var xPos = Math.floor(i/2)*4 + (4-k-1);
                    //   var yPos = (i%2)*4 + (j);
                    // } else if (i==5) {
                    //   var xPos = Math.floor(i/2)*4 + (4-k-1);
                    //   var yPos = (i%2)*4 + (4-j-1);
                    } else {
                      var xPos = Math.floor(i/2)*4 + (k);
                      var yPos = (i%2)*4 + (j);
                    }
                    var measuredVal, refVal;

                    measuredVal = jsonData.pressureData[i][j][k] - ghostLimits.pressureData[i][j][k];
                    refVal = oneKgRef.pressureData[i][j][k];

                    // Clip the minimum.
                    if (measuredVal<0) {
                      measuredVal = 0;
                    } else {
                      measuredVal + ghostLimits.pressureData[i][j][k];
                    }

                    var weight = weightScaling(measuredVal,refVal);

                    data.push({'x':xPos,'y':yPos,'value':weight, 'xScale': 1, 'yScale': 1 });

                    if (jsonData.pressureData[i][j][k]>100) {
                      console.log([i,j,k,measuredVal,refVal,weight]);
                    }
                    
                  }
                }
              }
              var xScaleFactor = 1.5;
              var yScaleFactor = 2;

              for (var i=0; i<hNo; i++) {
                for (var j=0; j<4; j++) {
                  for (var k=0; k<4; k++) {
                    var xPos = ((i*4) + k)*xScaleFactor;
                    var yPos = 10 + j*yScaleFactor;
                    
                    var measuredVal, refVal;

                    measuredVal = jsonData.humidityData[i][j][k] - ghostLimits.humidityData[i][j][k];
                    refVal = oneKgRef.humidityData[i][j][k];

                    // Clip the minimum.
                    if (measuredVal<0) {
                      measuredVal = 0;
                    } else {
                      measuredVal + ghostLimits.humidityData[i][j][k];
                    }

                    var mL = moistureScaling(measuredVal,refVal);

                    data.push({'x':xPos,'y':yPos,'value':mL, 'xScale': xScaleFactor, 'yScale': yScaleFactor });
                  }
                }
              }

              var x = 4*(pNo/2);
              var y = 20;
              
              // dim_1 = [];
              // dim_2 = [];
              // for (var i =0; i < x; i++) {
              //   for (var j =0; j < y; j++) {
              //     data.push({'x':i,'y':j,'value':maxNum*Math.random()});
              //   }
              // }

              // for (var i =0; i < x; i++) {
              //   dim_2.push(i);
              // }

              // for (var j =0; j < y; j++) {
              //   dim_1.push(j);
              // }

              gridSize = d3.min([width/x,height/y]);
              legendWidth = 25;

              // Redrawing. So remove everything in the svg first.
              svg.selectAll("*").remove();
              d3.select("body").selectAll(".d3-tip").remove();
              
              // Add tool tips.
              var tip = d3.tip()
                          .attr('class', 'd3-tip')
                          .style("visibility","visible")
                          .offset([-20, 0])
                          .html(function(d) {
                            return "Value:  <span style='color:red'>" + Math.round(d.value*100)/100;
                          });
                                    
              tip(svg.append("g"));

              // Add the tiles.
              var heatMap = svg.selectAll(".dim2")
                  .data(data)
                  .enter().append("rect")
                  .attr("x", function(d) { return (d.x) * gridSize; })
                  .attr("y", function(d) { return (d.y) * gridSize; })
                  .attr("rx", 4)
                  .attr("ry", 4)
                  .attr("class", "dim2 bordered")
                  .attr("width", function(d) { return (d.xScale) * gridSize - 2; })
                  .attr("height", function(d) { return (d.yScale) * gridSize - 2; })
                  .style("fill", function(d) { return colorScale(d.value); })
                  .attr("class", "square")
                  .on('mouseover', tip.show)
                  .on('mouseout', tip.hide);

                // heatMap.append("title").text(function(d) { return d.value; });
                    
                var legend = svg.selectAll(".legend")
                    .data([0].concat(colorScale.quantiles()), function(d) { return d; })
                    .enter().append("g")
                    .attr("class", "legend");

                legend.append("rect")
                  .attr("x", function(d, i) { return width-420; })
                  .attr("y", function(d, i) { return (i * legendWidth + 44); })
                  .attr("width", gridSize/2)
                  .attr("height", gridSize/2)
                  .style("fill", function(d, i) { return colors[i]; })
                  .attr("class", "square");

                legend.append("text")
                  .attr("class", "mono")
                  .text(function(d) { return "≥ " + Math.round(d*100)/100; })
                  .attr("x", function(d, i) { return width - 480; })
                  .attr("y", function(d, i) { return (i * legendWidth + 55); })

                var title = svg.append("text")
                      .attr("class", "mono")
                      .attr("x", width- 500)
                      .attr("y", 20)         
                      .style("font-size", "14px")
                      .text("Legend");

                // var dim1Labels = svg.selectAll(".dim1Label")
                //     .data(dim_1)
                //     .enter().append("text")
                //       .text(function (d) { return d; })
                //       .attr("x", 0)
                //       .attr("y", function (d, i) { return i * gridSize; })
                //       .style("text-anchor", "end")
                //       .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
                //       .attr("class","mono");

                // var dim2Labels = svg.selectAll(".dim2Label")
                //     .data(dim_2)
                //     .enter().append("text")
                //       .text(function(d) { return d; })
                //       .attr("x", function(d, i) { return i * gridSize; })
                //       .attr("y", 0)
                //       .style("text-anchor", "middle")
                //       .attr("transform", "translate(" + gridSize / 2 + ", -6)")
                //       .attr("class","mono");          
            });
            // setTimeout(update, 1000);
      }

      // update();
      
      // Timer function to keep updating.
      var myVar = setInterval(function(){ update(); }, 2000);

      //   heatMap.transition().style("fill", function(d,i) { return colorScale( newVal[i] ); });