/* TokenTagsVisualization */

var CharOffsets = require('./CharOffsets.js')

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

module.exports = TokenTagsVisualization
