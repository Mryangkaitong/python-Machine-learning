var React = window.React = require('react');

var SpansVisualization = require('./core/SpansVisualization.js')
var TokenTagsVisualization = require('./core/TokenTagsVisualization.js')
var EdgesVisualization = require('./core/EdgesVisualization.js')
var SentenceUtils = require('./core/SentenceUtils.js')

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

var DependenciesVisualization = function(element, source) {
    // compute sentenceTokenOffsets
    var sentenceTokenOffsets = SentenceUtils.getSentenceTokenOffsets(source.tokenOffsets, source.sentenceOffsets)
	return EdgesVisualization(element, source.tokenOffsets, source.sentenceOffsets, sentenceTokenOffsets, source.sentenceDependencies)
}

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

var TextWithAnnotations = React.createClass({

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
	    	details.push(<div className='extractionBlue'>{JSON.stringify(value)} </div>);
	    })
	    $.each(this.props.data._source, function(name, value) {
	      if (name != 'content' && name != 'id')
	        details.push (<div className='extraction'>{name} : {JSON.stringify(value)} </div>);
	    })
	}
    //style={{'white-space':'pre-wrap'}}  
    var div = (<div><span style={{'white-space':'pre-wrap'}} dangerouslySetInnerHTML={{__html: content}} />
        <br/><div style={{'color':'green'}}>{this.props.data._id}</div>
        {details}
    	</div>)

    return div;
  }
});

module.exports = TextWithAnnotations

