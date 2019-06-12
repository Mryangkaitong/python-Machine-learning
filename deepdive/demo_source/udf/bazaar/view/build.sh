#jsx view/ public/js
#browserify -t reactify public/js/main.js -o public/bundle.js
#browserify public/js/main.js -o public/bundle.js

browserify -t [ reactify --es6 ] view/main.jsx -o public/bundle.js
