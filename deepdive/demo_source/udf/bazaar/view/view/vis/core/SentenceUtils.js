var SentenceUtils = (function() {

    var FROM = 0
    var TO = 1

	var getSentenceTokenOffsets = function(tokenOffsets, sentenceOffsets) {
		var sentenceTokenOffsets = []
		var tokBegin = 0
		var tokEnd = 0
		for (var si = 0; si < sentenceOffsets.length; si++) {
			// move start
			while (tokenOffsets[tokBegin][FROM] < sentenceOffsets[si][FROM]) tokBegin++
			tokEnd = tokBegin
			while (tokEnd < tokenOffsets.length && tokenOffsets[tokEnd][FROM] <= sentenceOffsets[si][TO]) tokEnd++

			// now we have (tokBegin,tokEnd) for sentence
			sentenceTokenOffsets.push([tokBegin, tokEnd])
			tokBegin = tokEnd
		}
		return sentenceTokenOffsets
	}

	var findSentNumByTokenPos = function(pos, sentenceTokenOffsets) {
		var minIndex = 0;
		var maxIndex = sentenceTokenOffsets.length - 1;
		var currentIndex;
		var currentElement;

		while (minIndex <= maxIndex) {
		    currentIndex = (minIndex + maxIndex) / 2 | 0;
		    currentElement = sentenceTokenOffsets[currentIndex];

		    if (currentElement[TO] <= pos) {
		      //if (currentElement < searchElement) {
		       minIndex = currentIndex + 1;
		    }
		    else if (currentElement[FROM] > pos) {
		    	//if (currentElement > searchElement) {
		       maxIndex = currentIndex - 1;
		    }
		    else {
		       return currentIndex;
		    }
	    }
	}
	return {
		getSentenceTokenOffsets:getSentenceTokenOffsets,
		findSentNumByTokenPos:findSentNumByTokenPos
	};
})()

module.exports = SentenceUtils