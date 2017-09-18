/* Javascript for ReviewXBlock. */
function ReviewXBlock(runtime, element) {
  $(function ($) {
    /* Here's where you'd do things on page load. */
    'use strict'

    $('.button').on('click', function(event) {
      var $btn = $(event.currentTarget),
          $content = $btn.siblings('.content'),
          $iframe = $content.find('iframe');

      if ($iframe.attr('src') === '') {
          $iframe.attr('src', $btn.attr('data-iframe-src'));
      }

      // Toggle active state (+/-)
      $btn.toggleClass('button--active');

      // Toggle ARIA property
      // https://gist.github.com/toddmotto/bbb704d88cf39b06dbe0
      $btn.attr('aria-expanded', $btn.attr('aria-expanded') === 'true' ? 'false' : 'true');

      // Toggle active state (show/hide)
      $content.toggleClass('content--active');
    });

    $('.button').on('focus', function(event) {
      var $btn = $(event.currentTarget);
        $btn.attr('aria-selected', 'true');
    });

    $('.button').on('blur', function(event) {
      var $btn = $(event.currentTarget);
        $btn.attr('aria-selected', 'false');
    });
  });
}
