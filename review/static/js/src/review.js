/* Javascript for ReviewXBlock. */
function ReviewXBlock(runtime, element) {
    $(function ($) {
        /* Here's where you'd do things on page load. */
        'use strict'

        var App = {};
        App.buttonCount = 5;
        App.buttons = $('.button');

        [].forEach.call(App.buttons, function(button, i) {
            button.onclick = function () {
              var thisButton = this,
                  thisContent = $('[data-js=content]');
                
              // Toggle active state (+/-)
              thisButton.classList.toggle('button--active');
          
              // Toggle ARIA property
              // https://gist.github.com/toddmotto/bbb704d88cf39b06dbe0
              thisButton.setAttribute('aria-expanded', thisButton.getAttribute('aria-expanded') === 'true' ? 'false' : 'true');
          
              // Toggle active state (show/hide)
              thisContent[i].classList.toggle('content--active'); 
          
              // Toggle ARIA property    
              // TODO I think this is broken
              thisContent[i].setAttribute('aria-hidden', $('[data-js=content]')[4].getAttribute('aria-hidden') === 'true' ? 'false' : 'true');
            };
            
            // Keyboard navigation
            // http://www.w3.org/TR/2013/WD-wai-aria-practices-20130307/#accordion
            button.onfocus = function () {
              var thisButton = this;       
              
              // Set selected state
              [].forEach.call( $('[data-js=button]'), function(el) { 
                el.setAttribute('aria-selected', 'false');
                el.setAttribute('tabindex', '-1');
              });
              thisButton.setAttribute('aria-selected', 'true');
              thisButton.setAttribute('tabindex', '0'); 
            };
            
            button.onkeydown = function (e) {
              var thisButton = this;          
             
              switch(e.which) {
                // Left/Up
                case 37:
                case 38:
                  
                  e.preventDefault();
                  // Check for previous node
                            
                  if (!thisButton.parentNode.previousElementSibling) {
                    // No previous node,
                    // Set focus on last node
                    thisButton.parentNode.parentNode.getElementsByTagName('section')[App.buttonCount-1].getElementsByTagName('button')[0].focus();
                  } else {
                    // Move focus to previous
                    thisButton.parentNode.previousElementSibling.getElementsByTagName('button')[0].focus();
                  }
                  
                  break;
                  
                // Right/Down
                case 39:
                case 40:
                  e.preventDefault();
                  
                  // Check for next node
                 
                  if (!thisButton.parentNode.nextElementSibling) {
                    // No next node,
                    // Set focus on first node            
                    thisButton.parentNode.parentNode.getElementsByTagName('section')[0].getElementsByTagName('button')[0].focus();
                  } else {
                    // Move focus to next
                    thisButton.parentNode.nextElementSibling.getElementsByTagName('button')[0].focus();
                  }
                  break;
                  
                // Home
                case 36:          
                    // Set focus on first node
                  thisButton.parentNode.parentNode.getElementsByTagName('section')[0].getElementsByTagName('button')[0].focus();
                  break;
                  
                // End
                case 35:          
                    // Set focus on last node
                  thisButton.parentNode.parentNode.getElementsByTagName('section')[App.buttonCount-1].getElementsByTagName('button')[0].focus();
                  break;
                  
              }
            }; 
        });
    });
}
