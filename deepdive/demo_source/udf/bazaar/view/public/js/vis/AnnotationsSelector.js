
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

module.exports = AnnotationsSelector