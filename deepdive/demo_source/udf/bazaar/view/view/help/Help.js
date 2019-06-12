
var Help = React.createClass({


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
        //wrapperStyle.width = '300px'
    } else {
        //wrapperStyle.width = '0px'
        columnStyleBackground.width = '0px';
    }

    return (<div style={wrapperStyle}>
               <div className="help" style={columnStyle}>
                <h1>Query Examples</h1>

                <h3>Words and Phrases</h3>
                <code>quick</code> and <code>"quick brown"</code>

                <h3>Field names</h3>
                <code>_id:4325235</code><br />
                <code>title:(quick OR brown)</code><br />
                <code>book.\*:(quick brown)</code><br />
                <code>_missing_:title</code><br />
                <code>_exists_:title</code>

                <h3>Wildcards</h3>
                <code>qu?ck bro*</code>

                <h3>Regular Expressions</h3>
                <code>name:/joh?n(ath[oa]n)/</code>

                <h3>Fuzziness</h3>
                <code>quikc~ brwn~ foks~</code><br />
                <code>quikc~1</code>

                <h3>Proximity Searches</h3>
                <code>"fox quick"~5</code>

                <h3>Ranges</h3>
                <code>date:[2012-01-01 TO 2012-12-31]</code><br />
                <code>count:[1 TO 5]</code><br />
                <code>tag: {"{"}alpha TO omega{"}"}</code><br />
                <code>count:[10 TO *]</code><br />
                <code>date:{"{"}* TO 2012-01-01{"}"}</code><br />
                <code>count:[1 TO 5{"}"}</code><br />
                <code>age:&gt;=10</code><br />
                <code>age:(&gt;=10 AND &lt;20)</code>

                <h3>Boosting</h3>
                <code>quick^2 fox</code><br />
                <code>"john smith"^2</code><br />
                <code>(foo bar)^4</code>

                <h3>Boolean Operators</h3>
                <code>quick brown +fox -news</code><br />
                <code>((quick AND fox) OR (brown AND fox) OR fox) AND NOT news</code>

                <h3>Grouping</h3>
                <code>(quick OR brown) AND fox</code><br />
                <code>status:(active OR pending) title:(full text search)^2</code>

                <h3>Reserved Characters</h3>
                Escape with backslash<br />
                Example: <code>\(1\+1\)\=2</code> , finds (1+1)=2 <br />
                Characters: <code>+ - = &amp;&amp; || &gt; &lt; ! ( ) {"{"} {"}"} [ ] ^ &quot; ~ * ? : \ /</code>

                <h3>Empty Query</h3>
                Shows all results.

                <p>
                  For more details, see <a href="https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax" target="_blank">here</a>.
                </p>
                  </div>
                  <div style={columnStyleBackground}>
                    <div style={{position:'absolute', borderLeft:'1px solid white', minHeight:'100%', width:'1px'}}></div>
                  </div>
            	</div>)
  }
})

module.exports = Help
