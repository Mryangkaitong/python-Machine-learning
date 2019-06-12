var CharOffsets = require('./CharOffsets.js')

var is_chrome = navigator.userAgent.indexOf('Chrome') > -1;
var is_explorer = navigator.userAgent.indexOf('MSIE') > -1;
var is_firefox = navigator.userAgent.indexOf('Firefox') > -1;
var is_safari = navigator.userAgent.indexOf("Safari") > -1;
var is_Opera = navigator.userAgent.indexOf("Presto") > -1;
if ((is_chrome)&&(is_safari)) {is_safari=false;}
var is_explorer = (function() { return ((navigator.appName == 'Microsoft Internet Explorer') || ((navigator.appName == 'Netscape') && (new RegExp("Trident/.*rv:([0-9]{1,}[\.0-9]{0,})").exec(navigator.userAgent) != null))); })()

var DependenciesParameters = (function() {
  return {
	nextID: 0
  }
})()

var DependenciesDrawing = (function() {

	var getRightMostAnchor = function(anchors) {
		for (var i=anchors.length-1; i >= 0; i--) {
			if (anchors[i] != -1) {
				var v = anchors[i];
				anchors[i] = -1;
				return v;
			}
		}
	};

	var getLeftMostAnchor = function(anchors) {
		for (var i=0; i < anchors.length; i++) {
			if (anchors[i] != -1) {
				var v = anchors[i];
				anchors[i] = -1;
				return v;
			}
		}
	};

	var getTokenLeftsAndWidths = function(element, tokenOffsets, documentOffset) {
		if (!documentOffset) documentOffset = 0

		var FROM = 0
		var TO = 1

		// create a hidden element to keep entire article without wrap, then measure token dims and offsets
		var hidden, hiddenContainer;
		hiddenContainer = goog.dom.createDom('div',
				{'style':'position:absolute;width:0px;height:0px;overflow:hidden', 'class':'serif'} ,[
			hidden = goog.dom.createDom('div',
				{'style':'visibility:visible;white-space:nowrap;word-spacing:0px'})//
		]);
		var text = goog.dom.getRawTextContent(element[0]);
		var outers = new Array(), inners = new Array();

		for (var j=0, jj = tokenOffsets.length; j < jj; j++) {
			// token has offsets t.f, t.t
			var t = tokenOffsets[j];
			var outerEnd = (j < jj - 1)? tokenOffsets[j+1][FROM] - documentOffset: t[TO] - documentOffset;

			var tokenText = text.substring(t[FROM] - documentOffset, t[TO] - documentOffset);
			var whitespaceText = text.substring(t[TO] - documentOffset, outerEnd);
			var inner, outer;
			outer = goog.dom.createDom('span', {}, [
			      inner = goog.dom.createDom('span', {}, [
			           goog.dom.createTextNode(tokenText)
			      ]),
			      document.createTextNode(whitespaceText)
			]);
			hidden.appendChild(outer);
			outers.push(outer);
			inners.push(inner);
		}
		//document.body.appendChild(hiddenContainer);
		element.parent()[0].appendChild(hiddenContainer);

		var tokenLefts = new Array, tokenWidths = new Array();
        if (is_safari) {

            $.each(inners, function(i, value) {
                // note: we used to have
                //tokenLefts.push(value.offsetLeft);
                // here, but this gives pixel-precision, whereas the following gives subpixel-precision
                tokenLefts.push(value.getBoundingClientRect().left)
            });
            $.each(inners, function(i, value) {
                //tokenWidths.push(value.offsetWidth);
                tokenWidths.push(value.getBoundingClientRect().width)
            });
        } else {
            $.each(inners, function(i, value) {
                // note: we used to have
                tokenLefts.push(value.offsetLeft);
                // here, but this gives pixel-precision, whereas the following gives subpixel-precision
                //tokenLefts.push(value.getBoundingClientRect().left)
            });
            $.each(inners, function(i, value) {
                tokenWidths.push(value.offsetWidth);
                //tokenWidths.push(value.getBoundingClientRect().width)
            });
        }


//		goog.dom.removeNode(hiddenContainer);

		return [ tokenLefts, tokenWidths];
	};

	var createDrawing = function(name, deps, tokenLefts, tokenWidths) {

		/*   deps: [ {from:12,to:14}, {...}, ] */

		// convert to device pixels (for Retina displays)
		var devicePixelRatio = window.devicePixelRatio;
		var deviceTokenLefts = [], deviceTokenWidths = [];
		$.each(tokenLefts, function(i, value)
				{ deviceTokenLefts.push(value*devicePixelRatio); });
		$.each(tokenWidths, function(i, value)
				{ deviceTokenWidths.push(value*devicePixelRatio); });
		// not sure if this cast is necessary
		for (var i=0; i < deps.length; i++) {
			deps[i].from = parseInt(deps[i].from);
			deps[i].to = parseInt(deps[i].to);
		}

		// remove root
		var rootPos = -1;
		for (var i=0; i < deps.length; i++) {
			if (deps[i].from < 0 || deps[i].to < 0) rootPos = i;
		}
		if (rootPos >= 0) goog.array.removeAt(deps, rootPos);

		// determine anchor points on labels
		var len = deviceTokenWidths.length;
		var numAnchors = new Array(len);
		for (var i=0; i < len; i++) numAnchors[i] = 0;
		for (var i=0; i < deps.length; i++) {
			numAnchors[deps[i].from]++; numAnchors[deps[i].to]++; }
		var anchorXs = new Array(len);
		for (var i=0; i < len; i++) {
			var gap = deviceTokenWidths[i] / (numAnchors[i]+1);
			var ax = anchorXs[i] = new Array(numAnchors[i]);
			for (var j=0; j < numAnchors[i]; j++)
				ax[j] = deviceTokenLefts[i] + (1+j)*gap;
		}

		// sort deps by length
		goog.array.sort(deps, function(a,b) {
		    var l1 = Math.abs(a.to - a.from);
		    var l2 = Math.abs(b.to - b.from);
		    return l1 - l2;
		});

		var highestLevels = new Array(len-1);
		for (var i=0; i < highestLevels.length; i++) highestLevels[i] = 0;
		// for each dep, compute level
		for (var i=0; i < deps.length; i++) {
		    var d = deps[i];
		    var l = (d.from < d.to)? d.from : d.to;
		    var r = (d.from > d.to)? d.from : d.to;
		    var max = 0;
		    for (var j=l; j < r; j++)
		       max = Math.max(highestLevels[j],max);
		    d.level = (max+1);
		    for (var j=l; j < r; j++)
		       highestLevels[j] = (max+1);
		}

		// determine size of deps canvas
		var LEVEL_HEIGHT = 15*devicePixelRatio; //30;
		var max = 0;
		for (var i=0; i < highestLevels.length; i++)
		     max = Math.max(highestLevels[i], max);
		//var max_x = 0;
		//for (var i=0; i < x.length; i++)
		//     max_x = Math.max(x[i], max_x);
		var max_x = deviceTokenLefts[len-1] + deviceTokenWidths[len-1];
		var max_y = max*LEVEL_HEIGHT + 20;

		// invert levels (largest number is bottom, so we can later
		// just multiply with LEVEL_HEIGHT)
		for (var i=0; i < deps.length; i++) {
		    var d = deps[i];
		    d.level = max - d.level + 1;
		}

		// there's a hard limit on the dimensions of a canvas
		// (in Chrome, its 32,767 pixels)

		max_x = Math.min(32767, max_x);
		max_y = Math.min(32767, max_y);

		var ctx, canvas;
		if (document.getCSSCanvasContext) {
			ctx = document.getCSSCanvasContext("2d", name, max_x, max_y);
		} else {
			canvas = jQuery('<canvas id="' + name +'" width="' + max_x + '" height="' + max_y + '" style="display:none"></canvas>')
			$(document.body).append(canvas)
			ctx = canvas[0].getContext('2d');
		}


		//var ctx_highlight = document.getCSSCanvasContext("2d", name, max_x, max_y);

		// compute arc connection points
		var style = 'rgb(200,200,200)';
		for (var i=0; i < deps.length; i++) {
		    var d = deps[i];

		    //if (d.from < 0) continue; // ignore root dep

		    ctx.lineWidth = devicePixelRatio; //2;
		    ctx.lineJoin = 'miter';
		    ctx.strokeStyle=style;
		    ctx.beginPath();
		    var xto, xfrom;
		    // due to sentence length restriction, can't display all arcs
		    if (d.to >= anchorXs.length || d.from >= anchorXs.length)
		    	continue;
		    if (d.to > d.from) {
		    	xfrom = getRightMostAnchor(anchorXs[d.from]);
		    	xto = getLeftMostAnchor(anchorXs[d.to]);
			} else {
		    	xfrom = getLeftMostAnchor(anchorXs[d.from]);
		    	xto = getRightMostAnchor(anchorXs[d.to]);
			}
//		    if (xfrom >= 32767) {
//		    	console.log('POINT OUTSIDE ctx')
//		    	continue
//		    }
		    ctx.moveTo(xfrom, max_y);
		    ctx.lineTo(xfrom, d.level*LEVEL_HEIGHT+20);

		    if (Math.abs(xfrom - xto) < 40) {
		    	// the points are too close, draw one arc
		    	if (d.to > d.from)
		    		ctx.arc( xfrom + (xto - xfrom)/2, d.level*LEVEL_HEIGHT+20, (xto - xfrom)/2, Math.PI, 0, false);
		    	else if (d.to < d.from)
		    		ctx.arc( xto + (xfrom - xto)/2, d.level*LEVEL_HEIGHT+20, (xfrom - xto)/2, 0, Math.PI, true);
		    	else {
		    		//d.to == d.from
		    		console.log('WARNING: cannot handle special case where dependency goes from one token to itself')
		    	}
		    } else {
		    	// the points are further apart, draw two arcs connected by a straight line

			    if (d.to > d.from) {
			    	ctx.arc( xfrom+20, d.level*LEVEL_HEIGHT+20, 20, Math.PI, Math.PI*3/2, false);
			    	ctx.lineTo(xto-20, d.level*LEVEL_HEIGHT);
			    	ctx.arc( xto-20, d.level*LEVEL_HEIGHT+20, 20, Math.PI*3/2, 0, false);
				} else {
			    	ctx.arc( xfrom-20, d.level*LEVEL_HEIGHT+20, 20, 0, Math.PI*3/2, true);
			    	ctx.lineTo(xto+20, d.level*LEVEL_HEIGHT);
			    	ctx.arc( xto+20, d.level*LEVEL_HEIGHT+20, 20, Math.PI*3/2, Math.PI, true);
				}
		    }
		    ctx.lineTo(xto, max_y-2);

		    // draw arrow
		    ctx.moveTo(xto-3, max_y-5);
		    ctx.lineTo(xto, max_y-2);
		    ctx.lineTo(xto+3, max_y-5);
		    ctx.stroke();

		    // draw label
		    ctx.font = (devicePixelRatio*7) + 'pt Arial';
		    //ctx.font = '14pt Arial';
		    ctx.textAlign = 'center';
		    ctx.fillText(d.name, (xfrom+xto)/2, d.level*LEVEL_HEIGHT-4*devicePixelRatio);
		}


		//if (canvas) {
		//	var image = new Image();
		//	image.src = canvas.toDataURL("image/png");
		//}
//		return image;

//		var el = angular.element('<canvas id="' + name +'" width="' + max_x + '" height="' + max_y + ' style="display:none"></canvas>');
//		document.body.appendChild(el[0]);
//		console.log(document.body);


		return {
//			image:
			canvas:canvas,
			ctx:ctx,
			deviceWidth: max_x,
			deviceHeight: max_y,
			width: (max_x / devicePixelRatio),
			height: (max_y / devicePixelRatio),
			highestLevels: highestLevels,
			deviceTokenLefts: deviceTokenLefts,
			deviceTokenWidths: deviceTokenWidths
		};
	};

	return {
		getTokenLeftsAndWidths: getTokenLeftsAndWidths,
		createDrawing: createDrawing
	};
})()



var EdgesVisualization = function(element, tokenOffsets, sentenceOffsets, sentenceTokenOffsets, sentenceDependencies) {

	var state = {
	 	renderedSpans: new Array(),
	 	drawings:[],
	 	names:[],
	 	namePrefix:"prefix",
	 	destroyed: false
	};

	var createWithAnnotationsSentence = function(sentNum, state, element, renderedSpans, tokenOffsets, dependencies, tokenLefts, tokenWidths) {
		var nextID = DependenciesParameters.nextID
		DependenciesParameters.nextID = DependenciesParameters.nextID + 1
		var name = state.namePrefix + nextID
		state.names.push(name)

		// create canvas context
		var drawing = DependenciesDrawing.createDrawing(name,
				dependencies, tokenLefts, tokenWidths)

		state.drawings.push(drawing)

		var height = drawing.height
		var width = drawing.width;

		// refresh tokens with ctx info (show partial canvas for each token)
		$.each(renderedSpans, function(i, rs) {

			var firstSpan = rs.sels[0];
			var left = tokenLefts[i] - tokenLefts[0];

			var tokenWidth = (i < tokenLefts.length-1)? tokenLefts[i+1] - tokenLefts[i] : tokenWidths[i];

			if (is_safari) tokenWidth = tokenWidth + 1
                        var bg = ''
                        if (is_explorer) bg = 'background:url(' + drawing.canvas[0].toDataURL("image/png") + ') no-repeat -' + left + 'px 0px;';

			var el = goog.dom.createDom('div', { 'style' :
					'position:absolute;' +
					'top:-' + height + 'px;' +
					'left:0px;right:0px;' +
					//'z-index:-10;' +
					'z-index:0;' +
					'background:-webkit-canvas(' + name + ') no-repeat -' + left + 'px 0px;' +
					'background:-moz-element(#' + name + ') no-repeat -' + left + 'px 0px;' +
					bg +
//					'background:-moz-element(#jojo) no-repeat -' + left + 'px 0px;' +
					'background-size:' + width + 'px;' +
					'width:' + tokenWidth + 'px;' +
					'height:' + height + 'px'
			});
			// if you want all lines to be equal height, set marginTop as follows
			// var marginTop = height;
			var marginTop = (drawing.highestLevels[i]+1) * 15;
			// if you want to use inline rather than inline-block spans, use following line
			//$(firstSpan).attr('style', 'display:inline;line-height:' + (marginTop + 20) +
			//   'px;margin-top:' + marginTop + 'px;position:relative');
			$(firstSpan).attr('style', 'display:inline-block;margin-top:' + marginTop + 'px;position:relative')
			firstSpan.appendChild(el)
			rs.aux = new Array()
			rs.aux.push(el)
		}) //, this
	};

	var FROM = 0
	var TO = 1

	var createWithAnnotations = function(element, state, renderedSpans, tokenOffsets, sentenceOffsets, sentenceTokenOffsets, dependencies) {

		var documentOffset = 0 //scope.document.offset
		var documentTokenOffset = 0 //scope.document.tokenOffset

		var r = DependenciesDrawing.getTokenLeftsAndWidths($(element), tokenOffsets, documentOffset)
		var tokenLefts = r[0], tokenWidths = r[1];

		// insert spans
		CharOffsets.createMultiRangeSpans([element,this], tokenOffsets, renderedSpans, documentOffset)

		//var maxSentences = Math.min(25, sentenceTokenOffsets.length)
		var maxSentences = sentenceTokenOffsets.length
		//console.log('sentences ' + sentenceTokenOffsets.length)
		for (var sentNum = 0; sentNum < maxSentences; sentNum++) {
			var sto = sentenceTokenOffsets[sentNum]
			var lsto = [sto[FROM] - documentTokenOffset, sto[TO] - documentTokenOffset]
			if (lsto[FROM] >= lsto[TO]) continue
			var toks = tokenOffsets.slice(lsto[FROM], lsto[TO])
			var deps = dependencies[sentNum]
			var sntTokenLefts = tokenLefts.slice(lsto[FROM], lsto[TO])
			var shift = sntTokenLefts[0]
			for (var i=0; i < sntTokenLefts.length; i++)
				sntTokenLefts[i] = sntTokenLefts[i] - shift
			var sntTokenWidths = tokenWidths.slice(lsto[FROM], lsto[TO])
			var sntRenderedSpans = renderedSpans.slice(lsto[FROM], lsto[TO])
			createWithAnnotationsSentence(sentNum, state, element, sntRenderedSpans, toks, deps, sntTokenLefts, sntTokenWidths)
		}

    }


	// nothing to do
	if (tokenOffsets.length == 0) return

	//element.hide() // avoid reflows

	//var sentenceDependencies = 
	//var sentenceDependencies = [[{"from":0, "to":1, "name":"dep"},{"from":2, "to":1, "name":"dep"}]]
	createWithAnnotations(element, state, state.renderedSpans, tokenOffsets, sentenceOffsets, sentenceTokenOffsets, sentenceDependencies)
	//element.show()





	state.destroy = function() {
		if (state.destroyed) return;
		state.destroyed = true;
		$.each(state.renderedSpans, function(i, value) {
			// do bound listeners automatically get destroyed??
            //value.element.remove();
            //value.scope.$destroy();

			$.each(value.aux, function(j,n) {
				goog.dom.removeNode(n);
			});
			$.each(value.sels, function(j,n) {
				goog.dom.flattenElement(n);
			});
			value.sels = [];

		});
		goog.editor.range.normalizeNode(element);
		state.renderedSpans.length = 0; // clear array

		// need to destroy 2d context,
		// the following works, but is slow
		$.each(state.drawings, function(i, drawing) {
			var ctx = drawing.ctx;
			ctx.clearRect(0,0,drawing.deviceWidth,
					drawing.deviceHeight);
		});
		state.drawings = []
		state.names = []

		//element.remove();
		//goog.editor.range.normalizeNode(element[0]);
		//state.renderedSpans.length = 0;
	}
	return state

}

module.exports = EdgesVisualization
