/* Javascript for ReviewXBlock. */
function ReviewXBlock(runtime, element) {
  $(function ($) {
    'use strict'

    $('.review-button').on('click', function(event) {
      var $btn = $(event.currentTarget),
          $content = $btn.siblings('.review-content'),
          $iframe = $content.find('iframe'),
          title,
          skipLink,
          parser;

      if (!$btn.hasClass('disable-click')) {
        /*
        There is an issue where the buttons containing the review content
        could have multiple listeners on it causing it to remain closed when
        it was clicked on since the first listener would open it and the
        subsequent listener would immediately close it. This disables clicking
        for a short time so additional listeners can't happen
        Use case: In studio, every time you open the edit window, it attaches
        a new listener and then the above issue occurs.
        */
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
        parser = document.createElement('a');
        parser.setAttribute('id', 'iframe-hostname');
        parser.href = $btn.data('iframe-src');
        if (parser.hostname == window.location.hostname) {
          // Dynamically changes the height of the iFrame to the size of
          // the content inside. Sets the interval when the button is opened
          // and clears the interval when the button is closed
          if (!$btn.attr('class').includes('review-button--active')) {
            $btn.data('intervalID', setInterval(function() {
              $iframe.attr('height', $iframe['0'].contentWindow.document.body.offsetHeight + 'px');
            }, 1000));
          } else {
            clearInterval($btn.data('intervalID'));
          }

          // Need to wait for the iFrame to load so there is a body node
          $iframe['0'].addEventListener('load', function() {
            // Remove the 'skip to main content' link inside of an iFrame
            skipLink = $iframe['0'].contentDocument.body.querySelector('.nav-skip');
            $iframe['0'].contentDocument.body.removeChild(skipLink);
          });
        }
        $('#iframe-hostname').remove();

        // Toggle active state (+/-)
        $btn.toggleClass('review-button--active');

        // Toggle ARIA property
        // https://gist.github.com/toddmotto/bbb704d88cf39b06dbe0
        $btn.attr('aria-expanded', !$btn.attr('aria-expanded'));

        // Toggle active state (show/hide)
        $content.toggleClass('review-content--active');
      }
    });
  });
}
