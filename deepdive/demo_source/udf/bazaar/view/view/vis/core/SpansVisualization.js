/* TokensVisualization */
var CharOffsets = require('./CharOffsets.js')

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

module.exports = SpansVisualization