/* Javascript for ReviewXBlock. */
function ReviewXBlock(runtime, element) {
  $(function ($) {
    'use strict'

    $('.review-button').on('click', function(event) {
      var $btn = $(event.currentTarget),
          $content = $btn.siblings('.review-content'),
          $iframe = $content.find('iframe');

      if (!$btn.hasClass('disable-click')) {
        // Prevents double clicking which caused issues from seeing the problems
        $btn.addClass('disable-click');

        setTimeout(function() {
          $btn.removeClass('disable-click');
        }, 100);

        // iFrame loads after the button is clicked so there is not
        // a large amount of loading upon going to the xBlock
        if ($iframe.attr('src') === '') {
          $iframe.attr('src', $btn.data('iframe-src'));
        }


        // Prevent issues with cross-origin frames when in studio
        // (iFrames are hosted on courses.edx.org)
        if (window.location.hostname.indexOf("studio") == -1) {
          // Dynamically changes the height of the iFrame to the size of
          // the content inside
          if ($btn.attr('class').includes('review-button--active')) {
            clearInterval($btn.data('intervalID'));
          } else {
            $btn.data('intervalID', setInterval(function() {
              $iframe.attr('height', $iframe['0'].contentWindow.document.body.offsetHeight + 'px');
            }, 1000));
          }

          // Possible way to check if the iFrame loaded got a 404
          // This shouldn't happen, but is a possibility if course teams change
          // problems in their course before I have time to update the review course
          if ($iframe['0'].innerHTML) {
            var title = $iframe['0'].contentDocument.title.toLowerCase();
            if (title.indexOf("page not found")>=0 || title.indexOf("404")>=0) {
              // I would like to change the HTML to display some other message. Not sure if possible
              // I think an issue here is that it redirects the actual page.
              // Not sure how to handle that
              // $iframe.attr('src', '');
            }
          } else {
          }
        }

        // Toggle active state (+/-)
        $btn.toggleClass('review-button--active');

        // Toggle ARIA property
        // https://gist.github.com/toddmotto/bbb704d88cf39b06dbe0
        $btn.attr('aria-expanded', $btn.attr('aria-expanded') === 'true' ? 'false' : 'true');

        // Toggle active state (show/hide)
        $content.toggleClass('review-content--active');
      }
    });
  });
}
