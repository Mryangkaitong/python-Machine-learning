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
			var parentNode = t[0].parentNode
                        var parentNodeOffset = parentNode.readrOffset
              
			var el = goog.dom.createDom('span'); //, { 'style':'background-color:green'}); 
			range.surroundContents(el);
			//indexOffsets(t[0].parentNode, t[0].parentNode.readrOffset);
			indexOffsets(parentNode, parentNodeOffset);
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

module.exports = CharOffsets
