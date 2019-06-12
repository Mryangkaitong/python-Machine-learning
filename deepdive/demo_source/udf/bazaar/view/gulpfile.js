var browserify = require('browserify');
var gulp = require('gulp');
var gutil = require('gulp-util');
var source = require("vinyl-source-stream");
var reactify = require('reactify');
var es6ify = require('es6ify');
var watchify = require('watchify');

//var requireFiles = ['./node_modules/react/react.js']
var requireFiles = 'react-router'
var rename = require('gulp-rename');

function compileScripts(watch) {
    gutil.log('Starting browserify');

    var entryFile = './view/main.js';
    es6ify.traceurOverrides = {experimental: true};

    var bundler = browserify({entries: entryFile, debug: true});

    bundler.require(requireFiles);
    bundler.transform(reactify, {es6: true});
    bundler.transform(es6ify.configure(/.jsx/));

    var rebundle = function () {
        var stream = bundler.bundle();

        stream.on('error', function (err) { console.error(err) });
        stream = stream.pipe(source(entryFile));

        stream.pipe(rename('bundle.js'));
        stream.pipe(gulp.dest('public'));
    }
    bundler.on('update', rebundle);
    return rebundle();
}

gulp.task('default', [], function () {
    compileScripts(true);
});