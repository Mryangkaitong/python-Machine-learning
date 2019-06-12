
var AnnotationsSelector = React.createClass({

	render: function() {
		var onLayerChange = this.props.onLayerChange

		var buttons = this.props.layers.map(function(result) {
       		return (
         		<AnnotationsSelectorButton data={result} 
         			onLayerChange={onLayerChange} />
         	);
     	});
     	return (<div className="annotationsSelector">{buttons}</div>);
	}
});

var AnnotationsSelectorButton = React.createClass({
  handleClick: function() {
    var active = !this.props.data.active;
    this.props.onLayerChange(this.props.data.name, active);
  },
  render: function() {
    var classes = 'facet';
    if (!this.props.data.active)
      classes += ' facet-inactive';
    return (<div style={{fontSize:'10pt'}} className={classes} onClick={this.handleClick}>
       <div style={{display:'inline-block',width:'30px'}}>
         <i className="fa fa-check" ></i>
       </div>{this.props.data.name} 
     </div>)
  }
})

module.exports = AnnotationsSelector