
var Help = React.createClass({displayName: "Help",


  render: function() {
    var show = this.props.isHelp

    var wrapperStyle = {position:'fixed', top: '0px', right:0, minHeight:'100%', overflowX:'hidden', transition:'width .25s',
                               WebkitTransition:'width .25s', backgroundColor: 'rgb(71, 71, 71)'}
    var columnStyle = {position:'absolute', top:'50px', paddingTop:'10px', paddingBottom:'10px', paddingLeft:'10px', paddingRight:'10px',
                                      minHeight:'100%', width:'280px', color:'white', zIndex:3}

    var columnStyleBackground = {} //{position:'fixed', boxSizing:'borderBox', MozBoxSizing:'border-box', WebkitBoxSizing:'border-box',
                    //top:0, right:0, minHeight:'100%', backgroundColor:'rgba(71,71,71,1)', transition:'width .25s', WebkitTransition:'width .25s',
                    //zIndex:1}
    if (show) {
        columnStyleBackground.width = '300px'
        wrapperStyle.width = '300px'
    } else {
        wrapperStyle.width = '0px'
        columnStyleBackground.width = '0px';
    }

    return (React.createElement("div", {style: wrapperStyle}, 
               React.createElement("div", {className: "help", style: columnStyle}, 
                React.createElement("h1", null, "Query Examples"), 

                React.createElement("h3", null, "Words and Phrases"), 
                React.createElement("code", null, "quick"), " and ", React.createElement("code", null, "\"quick brown\""), 

                React.createElement("h3", null, "Field names"), 
                React.createElement("code", null, "_id:4325235"), React.createElement("br", null), 
                React.createElement("code", null, "title:(quick OR brown)"), React.createElement("br", null), 
                React.createElement("code", null, "book.\\*:(quick brown)"), React.createElement("br", null), 
                React.createElement("code", null, "_missing_:title"), React.createElement("br", null), 
                React.createElement("code", null, "_exists_:title"), 

                React.createElement("h3", null, "Wildcards"), 
                React.createElement("code", null, "qu?ck bro*"), 

                React.createElement("h3", null, "Regular Expressions"), 
                React.createElement("code", null, "name:/joh?n(ath[oa]n)/"), 

                React.createElement("h3", null, "Fuzziness"), 
                React.createElement("code", null, "quikc~ brwn~ foks~"), React.createElement("br", null), 
                React.createElement("code", null, "quikc~1"), 

                React.createElement("h3", null, "Proximity Searches"), 
                React.createElement("code", null, "\"fox quick\"~5"), 

                React.createElement("h3", null, "Ranges"), 
                React.createElement("code", null, "date:[2012-01-01 TO 2012-12-31]"), React.createElement("br", null), 
                React.createElement("code", null, "count:[1 TO 5]"), React.createElement("br", null), 
                React.createElement("code", null, "tag: ", "{", "alpha TO omega", "}"), React.createElement("br", null), 
                React.createElement("code", null, "count:[10 TO *]"), React.createElement("br", null), 
                React.createElement("code", null, "date:", "{", "* TO 2012-01-01", "}"), React.createElement("br", null), 
                React.createElement("code", null, "count:[1 TO 5", "}"), React.createElement("br", null), 
                React.createElement("code", null, "age:>=10"), React.createElement("br", null), 
                React.createElement("code", null, "age:(>=10 AND <20)"), 

                React.createElement("h3", null, "Boosting"), 
                React.createElement("code", null, "quick^2 fox"), React.createElement("br", null), 
                React.createElement("code", null, "\"john smith\"^2"), React.createElement("br", null), 
                React.createElement("code", null, "(foo bar)^4"), 

                React.createElement("h3", null, "Boolean Operators"), 
                React.createElement("code", null, "quick brown +fox -news"), React.createElement("br", null), 
                React.createElement("code", null, "((quick AND fox) OR (brown AND fox) OR fox) AND NOT news"), 

                React.createElement("h3", null, "Grouping"), 
                React.createElement("code", null, "(quick OR brown) AND fox"), React.createElement("br", null), 
                React.createElement("code", null, "status:(active OR pending) title:(full text search)^2"), 

                React.createElement("h3", null, "Reserved Characters"), 
                "Escape with backslash", React.createElement("br", null), 
                "Example: ", React.createElement("code", null, "\\(1\\+1\\)\\=2"), " , finds (1+1)=2 ", React.createElement("br", null), 
                "Characters: ", React.createElement("code", null, "+ - = && || > < ! ( ) ", "{", " ", "}", " [ ] ^ \" ~ * ? : \\ /"), 

                React.createElement("h3", null, "Empty Query"), 
                "Shows all results.", 

                React.createElement("p", null, 
                  "For more details, see ", React.createElement("a", {href: "https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax", target: "_blank"}, "here"), "."
                )
                  ), 
                  React.createElement("div", {style: columnStyleBackground}, 
                    React.createElement("div", {style: {position:'absolute', borderLeft:'1px solid white', minHeight:'100%', width:'1px'}})
                  )
            	))
  }
})

module.exports = Help
