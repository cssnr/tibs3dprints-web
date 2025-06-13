const gulp = require('gulp')
// const download = require('gulp-download2')

gulp.task('animate', () => {
    return gulp
        .src('node_modules/animate.css/animate.min.css')
        .pipe(gulp.dest('app/static/dist/animate'))
})

gulp.task('bootstrap', () => {
    return gulp
        .src([
            // 'node_modules/bootstrap/dist/css/bootstrap.min.css',
            'node_modules/bootstrap/dist/js/bootstrap.bundle.min.js',
        ])
        .pipe(gulp.dest('app/static/dist/bootstrap'))
})

gulp.task('clipboard', () => {
    return gulp
        .src('node_modules/clipboard/dist/clipboard.min.js')
        .pipe(gulp.dest('app/static/dist/clipboard'))
})

gulp.task('fontawesome', () => {
    return gulp
        .src(
            [
                'node_modules/@fortawesome/fontawesome-free/css/all.min.css',
                'node_modules/@fortawesome/fontawesome-free/js/all.min.js',
                'node_modules/@fortawesome/fontawesome-free/webfonts/**/*',
            ],
            {
                base: 'node_modules/@fortawesome/fontawesome-free',
                encoding: false,
            }
        )
        .pipe(gulp.dest('app/static/dist/fontawesome'))
})

gulp.task('jquery', () => {
    return gulp
        .src('node_modules/jquery/dist/jquery.min.js')
        .pipe(gulp.dest('app/static/dist/jquery'))
})

gulp.task('js-cookie', () => {
    return gulp
        .src('node_modules/js-cookie/dist/js.cookie.min.js')
        .pipe(gulp.dest('app/static/dist/js-cookie'))
})

gulp.task('uppy', () => {
    return download([
        'https://releases.transloadit.com/uppy/v3.27.0/uppy.min.mjs',
        'https://releases.transloadit.com/uppy/v3.27.0/uppy.min.css',
    ]).pipe(gulp.dest('app/static/dist/uppy'))
})

gulp.task(
    'default',
    gulp.parallel(
        'animate',
        'bootstrap',
        'clipboard',
        'fontawesome',
        'jquery',
        'js-cookie'
        // 'uppy'
    )
)
