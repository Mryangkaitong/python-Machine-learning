

var CharOffsets = (function() {
	var ELEMENT = 1;
	var TEXT = 3;
	
	var offsetComparator = function(e1, e2) {
		return e1.readrOffset - e2.readrOffset;					
	};
		
	var indexOffsets = function(node, offset) {
		node.readrOffset = offset;
		if (node.nodeType == TEXT) {
			node.readrLength = node.nodeValue.length;
		} else if (node.nodeType == ELEMENT) {
			// ignore if has class ignoreReadrLength
			if (goog.dom.classes.has(node, 'ignoreReadrLength')) {
				node.readrLength = 0;
			} else {
				// sum up lengths of children
				var l = 0;
				for (var i=0, ii = node.childNodes.length; i < ii; i++) {
					var child = node.childNodes[i];
					indexOffsets(child, offset + l);
					l += child.readrLength;
				}
				node.readrLength = l;
			}
		}
	};
	
	var getTextRangesToHighlightFromIndex = function(node, start, end) {
		var results = new Array();
		recur(node, start, end, results);
		return results;
	};
	
	var recur = function(node, start, end, results) {
		if (end - start <= 0) return;
	
		// we assume that start >= node.readrOffset and end <= node.readrOffset + node.readrLength
		if (node.nodeType == TEXT) {
			results.push([node, start - node.readrOffset, end - node.readrOffset, start, end]);
			return;
		}
		// binary search for start and end
		var ns = goog.array.binarySearch(node.childNodes, { readrOffset : start }, offsetComparator);
		var ne = goog.array.binarySearch(node.childNodes, { readrOffset : end }, offsetComparator);
		
		if (ns < 0) { ns = -ns-2; }
		if (ne < 0) { ne = -ne-1; }
		
		for (var i=ns; i < ne; i++) {
			var child = node.childNodes[i];
			var s = (i==ns)? start : child.readrOffset;
			var e = (i==ne-1)? end : child.readrOffset + child.readrLength;
			
			recur(child, s, e, results);
		}
	};
	
	var createMultiRangeSpans = function(element, tokenOffsets, renderedSpans, documentOffset) {
		if (!renderedSpans)
			renderedSpans = new Array();
		if (!documentOffset)
			documentOffset = 0
		indexOffsets(element[0], documentOffset)
		for (var j=0, jj = tokenOffsets.length; j < jj; j++) {
			// token has offsets t.f, t.t
			var rs = createSingleRangeSpans(element, tokenOffsets[j]);
			renderedSpans.push(rs);
		}
		return renderedSpans;
	};

    var FROM = 0
    var TO = 1
	
	// example tokenOffset: { f:12, t:23 }
	var createSingleRangeSpans = function(element, tokenOffset) {
		//if (!documentOffset) 
			//documentOffset = 0
		var sels = new Array();
		var todo = getTextRangesToHighlightFromIndex
			(element[0], tokenOffset[FROM], tokenOffset[TO]);
		for (var i=0, ii = todo.length; i < ii; i++) {
			var t = todo[i];
			var range = goog.dom.Range.createFromNodes(t[0], t[1], t[0], t[2]);
			var el = goog.dom.createDom('span'); //, { 'style':'background-color:green'}); 
			range.surroundContents(el);
			indexOffsets(t[0].parentNode, t[0].parentNode.readrOffset);
			sels.push(el);
		}
		return { sels:sels };
	};
	
	//note, the output of this function is a singleton
	return {
		indexOffsets: indexOffsets,
		getTextRangesToHighlightFromIndex: getTextRangesToHighlightFromIndex,
		createMultiRangeSpans: createMultiRangeSpans,
		createSingleRangeSpans: createSingleRangeSpans
	};
})()

/* TokensVisualization */

var Span = function(sels) {
    var state = {}

	var fragment = function(i, length) {
		var fragment = '';
		if (i==0 && i < length-1) fragment = 'left';
		else if (i==0 && i==length-1) fragment = 'leftright';
		else if (i==length-1 && i > 0) fragment = 'right';
		else if (i > 0 && i < length-1) fragment = 'inner';
		return fragment;
	};

    // initialize
    state.sels = sels
    state.color = 'red'
	if (!sels) return;
	var ii = sels.length;
	$.each(sels, function(i, sel) {
		$(sel).addClass('highlight_' + state.color);
		$(sel).addClass('highlight_' + fragment(i, ii));
		//$(sel).on('click', function() {
		//	console.log('clicked');
		//});
    })

    state.destroy = function() {
    	// unbind all handlers
		if (!state.sels) return;
				
		$.each(state.sels, function(sel) {
			//$(sel).unbind('click');
		});
    }
    return state
}


var SpansVisualization = function(element, spans) {
	var state = {
	 	renderedSpans: new Array(),
	 	destroyed: false
	};

	//var documentOffset = scope.document.offset
	var documentOffset = 0
		
	CharOffsets.createMultiRangeSpans([element,this], spans, state.renderedSpans, documentOffset)

	$.each(state.renderedSpans, function(i, rs) {
		var span = new Span(rs.sels)
	});

	state.destroy = function() {
		state.destroyed = true;
		$.each(state.renderedSpans, function(i, value) {
			// do bound listeners automatically get destroyed??
            //value.element.remove();
            //value.scope.$destroy();

			//$.each(value.aux, function(j,n) {
			//	goog.dom.removeNode(n);
			//});
			$.each(value.sels, function(j,n) {
				goog.dom.flattenElement(n);
			});
			value.sels = [];			
		});
		//element.remove();
		//goog.editor.range.normalizeNode(element[0]);
		state.renderedSpans.length = 0;     
	}
	return state
}

/* TokenTagsVisualization */


var TokenTagsVisualization = function(element, tokenOffsets, tags) {
	var state = {
	 	renderedSpans: new Array(),
	 	destroyed: false
	};

	//var documentOffset = scope.document.offset
	var documentOffset = 0
		
	// insert spans
	CharOffsets.createMultiRangeSpans([element,this], tokenOffsets, state.renderedSpans, documentOffset)

	$.each(state.renderedSpans, function(i, rs) {
		var firstSpan = rs.sels[0]
		var el = goog.dom.createDom('div', { 'style' :
			'position:absolute;' +
			'top:-15px;' +
			'left:0px;right:0px;' +
			'z-index:0;' +
			'width:100px;' + //' + tokenWidth + 'px;' +
			'height:20px;' +
			'color:red;' +
			'font-size:10px;' +
			'font-family:helvetica,arial;' +
			'font-stretch:semi-condensed;' +
			'font-weight:500;'/* +
			'background-color:white'*/
		})
		el.appendChild(goog.dom.createTextNode(tags[i]))
		// if you want all lines to be equal height, set marginTop as follows
		//var marginTop = (drawing.highestLevels[i]+1) * 15;			
			// if you want to use inline rather than inline-block spans, use following line
			//$(firstSpan).attr('style', 'display:inline;line-height:' + (marginTop + 20) + 
			//   'px;margin-top:' + marginTop + 'px;position:relative');
		var marginTop = 10
		$(firstSpan).attr('style', 'display:inline-block;margin-top:' + marginTop + 'px;position:relative')
		firstSpan.appendChild(el)
		rs.aux = new Array()
		rs.aux.push(el)
		})

	state.destroy = function() {
		state.destroyed = true;
		$.each(state.renderedSpans, function(i, value) {
			$.each(value.aux, function(j, n) {
				goog.dom.removeNode(n);
			})
			$.each(value.sels, function(j, n) {
				goog.dom.flattenElement(n);				
			})
			value.sels = [];			
		});
		//element.remove();
		//goog.editor.range.normalizeNode(element[0]);
		state.renderedSpans.length = 0;		
	}
	return state
}



var TokensVisualization = function(element, source) {
	return SpansVisualization(element, source.tokenOffsets)
}

var SentencesVisualization = function(element, source) {
	return SpansVisualization(element, source.sentenceOffsets)
}

var PartOfSpeechVisualization = function(element, source) {
	return TokenTagsVisualization(element, source.tokenOffsets, source.poss)
}

var LemmasVisualization = function(element, source) {
	return TokenTagsVisualization(element, source.tokenOffsets, source.lemmas)
}


/* DependenciesVisualization */

/* FramesVisualization */

// var find = function(arr, name) {
// 	var el
// 	$.each(arr, function(i,v) {
// 		if (v.name == name) {
// 			el = v
// 			return false
// 		}
// 	})
// 	return el 
// }

var ExtractorsVisualization = function(element, source, annotations) {
   var sentenceTokenOffsets = source['sentenceTokenOffsets']
   var tokenOffsets = source['tokenOffsets']
   var extractorOffsets = []

   $.each(annotations, function(i, a) {
   	  var sentNum = a.range.sentNum
   	  var sentenceBeginToken = sentenceTokenOffsets[sentNum][0]
   	  var tokenFrom = sentenceBeginToken + a.range.f
   	  var tokenTo = sentenceBeginToken + a.range.t
      var charFrom = tokenOffsets[tokenFrom][0]
      var charTo = tokenOffsets[tokenTo - 1][1]
      extractorOffsets.push([charFrom,charTo])
   })
   return SpansVisualization(element, extractorOffsets)
}




var TextWithAnnotations = React.createClass({displayName: "TextWithAnnotations",

  componentDidMount: function() {
  	this.vis = {}
  	this.buildCustomDom()
  },
  componentDidUpdate: function() {
  	this.buildCustomDom()
  },
  buildCustomDom: function() {
    var div = React.findDOMNode(this)
    //cleanup existing visualizations
    $.each(this.vis, function(k,v) { v.destroy() })

  	this.vis = {}

    var annotations = this.props.data.annotations
    var sourceData = this.props.data._source
    var vis = this.vis

    $.each(this.props.layers, function(i, l) {
        if (vis && vis[l.name] && !l.active) {
        	vis[l.name].destroy()
        	delete vis[l.name]
        }
        if (vis && !vis[l.name] && l.active) {
        	if (l.name == 'Tokens')
        		vis[l.name] = new TokensVisualization(div, sourceData)
        	if (l.name == 'Sentences')
        		vis[l.name] = new SentencesVisualization(div, sourceData)
        	if (l.name == 'Extractors')
        		vis[l.name] = new ExtractorsVisualization(div, sourceData, annotations)
        	if (l.name == 'Dependencies')
        		vis[l.name] = new DependenciesVisualization(div, sourceData)
        	if (l.name == 'Lemmas')
        		vis[l.name] = new LemmasVisualization(div, sourceData)        		
        	if (l.name == 'PartOfSpeech')
        		vis[l.name] = new PartOfSpeechVisualization(div, sourceData)        		
        }
    })
  },
  isActive: function(name) {
  	var isActive = false
    $.each(this.props.layers, function(i, l) {
       if (l.name == name) { isActive = l.active; return false }
    })
    return isActive
  },

  render: function() {
    content = this.props.data._source.content;
    // if we have field with keyword highlighting, take that
    if (this.props.data.highlight != null &&
        this.props.data.highlight.content != null) {
      content = this.props.data.highlight.content[0];
    }
    var details = []
    if (this.isActive('Details')) {
	    $.each(this.props.data.annotations, function(i, value) {
	    	details.push(React.createElement("div", {className: "extractionBlue"}, JSON.stringify(value), " "));
	    })
	    $.each(this.props.data._source, function(name, value) {
	      if (name != 'content' && name != 'id')
	        details.push (React.createElement("div", {className: "extraction"}, name, " : ", JSON.stringify(value), " "));
	    })
	}

    var div = (React.createElement("div", null, React.createElement("span", {dangerouslySetInnerHTML: {__html: content}}), 
        React.createElement("br", null), React.createElement("div", {style: {'color':'green'}}, this.props.data._id), 
        details
    	))

    return div;
  }
});


var AnnotationsSelector = React.createClass({displayName: "AnnotationsSelector",

	render: function() {
		var onLayerChange = this.props.onLayerChange

		var buttons = this.props.layers.map(function(result) {
       		return (
         		React.createElement(AnnotationsSelectorButton, {data: result, 
         			onLayerChange: onLayerChange})
         	);
     	});
     	return (React.createElement("div", {className: "annotationsSelector"}, buttons));
	}
});

var AnnotationsSelectorButton = React.createClass({displayName: "AnnotationsSelectorButton",
  handleClick: function() {
    var active = !this.props.data.active;
    this.props.onLayerChange(this.props.data.name, active);
  },
  render: function() {
    var classes = 'facet';
    if (!this.props.data.active)
      classes += ' facet-inactive';
    return (React.createElement("div", {style: {fontSize:'10pt'}, className: classes, onClick: this.handleClick}, 
       React.createElement("div", {style: {display:'inline-block',width:'30px'}}, 
         React.createElement("i", {className: "fa fa-check"})
       ), this.props.data.name
     ))
  }
})

